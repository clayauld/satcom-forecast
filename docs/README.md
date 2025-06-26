# SatCom Forecast Documentation

This directory contains documentation for the SatCom Forecast Home Assistant integration.

## Files

- **`format_comparison.md`** - Detailed comparison of the three forecast formats (Summary, Compact, Full)
- **`README.md`** - This file

## Format Comparison

The `format_comparison.md` file provides a comprehensive overview of:

- **Summary Format**: Concise 150-character summaries with pipe separators and standard abbreviations (Tngt, Aft)
- **Compact Format**: Detailed multi-line format with weather highlights and advanced smoke detection
- **Full Format**: Complete NOAA forecast text

### Key Features Documented

- **Standard Abbreviations**: "Tngt" for Tonight, "Aft" for This Afternoon
- **Advanced Smoke Detection**: Areas of smoke (65%), wildfire smoke (75%), heavy smoke (90%), widespread haze (50%)
- **Weather Event Detection**: Comprehensive detection of rain, snow, wind, thunderstorms, fog, and smoke
- **Probability Inference**: Smart percentage assignment when NOAA doesn't specify
- **Extreme Event Highlighting**: 🚨 indicators for dangerous conditions

Each format is designed for different use cases and display requirements, with the Summary format optimized for satellite communication constraints. 