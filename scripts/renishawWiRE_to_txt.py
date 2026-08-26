"""Convert a Renishaw WiRE WDF spectrum or map to a text file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterator

import numpy as np
from renishawWiRE import WDFReader
from renishawWiRE.types import MeasurementType


def next_output_path(wdf_path: Path) -> Path:
	"""Return a non-existing TXT path beside the input WDF."""
	candidate = wdf_path.with_suffix(".txt")
	suffix = 1
	while candidate.exists():
		candidate = wdf_path.with_name(f"{wdf_path.stem}_{suffix}.txt")
		suffix += 1
	return candidate


def spectrum_rows(reader: WDFReader) -> Iterator[tuple[int, tuple[float, ...]]]:
	"""Yield valid output rows, one spectrum at a time."""
	wavenumbers = np.asarray(reader.xdata)
	spectra = np.asarray(reader.spectra)
	is_mapping = reader.measurement_type == MeasurementType.Mapping

	if spectra.ndim == 1:
		spectra = spectra.reshape(1, -1)
	elif spectra.ndim == 3:
		spectra = spectra.reshape(-1, spectra.shape[-1])
	elif spectra.ndim != 2:
		raise ValueError(f"unsupported spectrum shape: {spectra.shape}")

	if wavenumbers.ndim != 1:
		raise ValueError("the WDF wavenumber data is not one-dimensional")

	coordinates: list[tuple[float, float]] = []
	if is_mapping:
		x_positions = np.asarray(getattr(reader, "xpos"))
		y_positions = np.asarray(getattr(reader, "ypos"))
		if len(x_positions) != len(spectra) or len(y_positions) != len(spectra):
			raise ValueError("map coordinates do not match the number of spectra")
		coordinates = list(zip(x_positions, y_positions))

	for index, spectrum in enumerate(spectra):
		try:
			if spectrum.ndim != 1 or len(spectrum) != len(wavenumbers):
				raise ValueError("spectrum length does not match wavenumber data")
			values = np.asarray(spectrum, dtype=float)
			shifts = np.asarray(wavenumbers, dtype=float)
			if not np.isfinite(values).all() or not np.isfinite(shifts).all():
				raise ValueError("spectrum contains non-finite values")

			if is_mapping:
				x_position, y_position = coordinates[index]
				if not np.isfinite(x_position) or not np.isfinite(y_position):
					raise ValueError("spectrum has non-finite coordinates")
				for row in zip(
					(float(x_position),) * len(shifts),
					(float(y_position),) * len(shifts),
					shifts,
					values,
				):
					yield index, row
			else:
				for row in zip(shifts, values):
					yield index, row
		except (TypeError, ValueError, IndexError):
			continue


def convert(wdf_path: Path, output_path: Path) -> tuple[int, int]:
	"""Convert *wdf_path* and return (converted spectra, skipped spectra)."""
	reader = WDFReader(wdf_path)
	spectra = np.asarray(reader.spectra)
	expected_spectra = 1 if spectra.ndim == 1 else spectra.shape[0]
	if spectra.ndim == 3:
		expected_spectra = spectra.shape[0] * spectra.shape[1]

	converted = 0
	valid_indices: set[int] = set()
	try:
		is_mapping = reader.measurement_type == MeasurementType.Mapping
		header = "X Y RamanShift Intensity\n" if is_mapping else "RamanShift Intensity\n"
		with output_path.open("w", encoding="utf-8", newline="") as output_file:
			output_file.write(header)
			for spectrum_index, row in spectrum_rows(reader):
				if is_mapping:
					output_file.write("{:.10g} {:.10g} {:.10g} {:.10g}\n".format(*row))
				else:
					output_file.write("{:.10g} {:.10g}\n".format(*row))
				valid_indices.add(spectrum_index)
	finally:
		reader.close()

	converted = len(valid_indices)
	skipped = max(expected_spectra - converted, 0)
	return converted, skipped


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("wdf_file", type=Path, help="Renishaw WiRE .wdf file")
	args = parser.parse_args()
	wdf_path = args.wdf_file.expanduser().resolve()

	if not wdf_path.is_file():
		parser.error(f"input file does not exist: {wdf_path}")

	output_path = next_output_path(wdf_path)
	try:
		converted, skipped = convert(wdf_path, output_path)
	except (AttributeError, OSError, ValueError, TypeError) as error:
		parser.error(str(error))

	print(f"Converted {converted} grid points/spectra; skipped {skipped}.")
	print(f"Output: {output_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
