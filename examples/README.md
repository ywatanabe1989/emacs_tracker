<!-- ---
!-- Timestamp: 2025-08-24 22:27:41
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/emacs_tracker/examples/README.md
!-- --- -->

# Sample Tracking Data Examples

This directory contains realistic examples of tracking data captured by the emacs-tracker-context. These examples demonstrate the comprehensive tracking capabilities and data structures.

## 📁 Available Examples

### 1. `coding_session_20250824_1147.json` - Machine Learning Development
**Duration:** 45.3 minutes | **Interactions:** 127 | **Files:** 5

A comprehensive coding session showing a developer working on a machine learning project:
- **Python development** with code modifications and debugging comments
- **Data exploration** with large CSV file (50,000 rows, 15MB)
- **Visualization review** of PNG results from matplotlib
- **Audio processing** inspection of WAV training data (50MB, 44.1kHz)
- **Multi-modal workflow** switching between code, data, images, and audio

**Key Features Demonstrated:**
- Real-time content diff tracking
- Media file property analysis (DPI, sampling rates, resolution)
- Large file handling and performance impact tracking
- Hash-based change detection
- Multi-window multitasking patterns

### 2. `writing_session_20250824_1130.json` - Academic Writing
**Duration:** 25.8 minutes | **Interactions:** 89 | **Files:** 3

An academic writing session in Org-mode with research integration:
- **Structured document editing** with Org-mode outline navigation
- **Reference management** with BibTeX integration
- **Figure insertion** and cross-document linking
- **Academic formatting** with proper citation styles
- **SVG diagram review** for publication-ready figures

**Key Features Demonstrated:**
- Org-mode specific context tracking
- Academic workflow patterns
- Cross-document reference linking
- Vector graphics analysis
- High-DPI display adaptation (144 DPI, 2560x1440)

### 3. `debugging_session_20250824_1400.json` - Systematic Debugging
**Duration:** 32.5 minutes | **Interactions:** 203 | **Files:** 5

A debugging session showing systematic problem-solving workflow:
- **Error reproduction** and stack trace analysis
- **REPL-driven debugging** with Python interactive shell
- **Test-driven fixes** with pytest execution
- **Log file analysis** of large error logs (125MB)
- **Defensive programming** with null checks and error handling

**Key Features Demonstrated:**
- High-frequency interaction patterns (14.8 switches/minute)
- Multi-buffer debugging workflow
- Compilation buffer integration
- Large log file navigation
- Ultra-wide display utilization (3440x1440)

## 🏗️ Data Structure Overview

Each session file contains:

```json
{
  "session_metadata": {
    "session_id": "unique_session_identifier",
    "duration_minutes": 45.3,
    "total_interactions": 127,
    "environment": {
      "display": {"resolution": "1920x1080", "dpi": 96},
      "emacs": {"font_family": "Consolas", "font_size": 12}
    }
  },
  "tracked_sequence": [
    {
      "timestamp": "2025-08-24T11:47:15.123456",
      "buffer": { /* Buffer context */ },
      "cursor": { /* Position and movement */ },
      "commands": { /* Emacs commands executed */ },
      "changes": { /* Diff and change analysis */ },
      "media_analysis": { /* File-specific properties */ }
    }
  ],
  "session_summary": {
    "productivity_metrics": { /* Quantitative analysis */ },
    "tracked_patterns": { /* Qualitative insights */ },
    "technical_context": { /* Project and tool context */ }
  }
}
```

## 📊 Media File Properties Tracked

### Images
- **DPI/Resolution:** 72-300 DPI, various pixel dimensions
- **Color depth:** 24-bit, sRGB color space
- **Format details:** PNG, SVG with compression info
- **Quality assessment:** Publication-ready vs web-optimized

### Audio Files
- **Sampling rates:** 44.1kHz (CD quality) to 96kHz (studio)
- **Bit depth:** 16-bit to 24-bit
- **Channel configuration:** Mono, stereo, 5.1 surround
- **Codec information:** WAV PCM, MP3, FLAC

### Video Files
- **Resolution:** 1080p to 4K with frame rate data
- **Codec details:** H.264, HEVC with bitrate info
- **Audio tracks:** Separate audio codec tracking
- **Quality metrics:** HDR, color space information

## 🔍 Tracking Pattern Analysis

### Workflow Types Captured
1. **Exploratory Development** - High context switching, multiple file types
2. **Structured Academic Writing** - Deep focus periods, reference integration
3. **Systematic Debugging** - Rapid iteration, tool integration

### Productivity Metrics
- **Focus Duration:** Average time spent in each buffer
- **Context Switching:** Frequency and pattern analysis
- **Multitasking Intensity:** Window management and parallel work
- **File Navigation Efficiency:** Movement patterns and shortcuts usage

### Technical Context
- **Project Classification:** ML, academic, web development
- **Tool Integration:** REPL, testing, compilation, version control
- **File Ecosystem:** Programming languages, data formats, media types

## 🎯 Use Cases for AI Agents

These examples enable AI agents to:

### Content-Aware Assistance
```python
# Example: Detect high-resolution images needing compression
if media_properties["dpi_x"] > 150 and context["workflow"] == "web_development":
    suggest("Consider compressing images for web use")
```

### Workflow Optimization
```python
# Example: Identify inefficient context switching
if metrics["context_switches_per_minute"] > 10:
    suggest("Consider using window layouts to reduce switching")
```

### Quality Assurance
```python
# Example: Ensure consistent audio quality
audio_files = get_files_by_type("audio")
if varying_sample_rates(audio_files):
    suggest("Standardize audio sample rates for consistency")
```

## 🚀 Generating Your Own Examples

To capture real tracking data:

1. **Start the MCP server:**
   ```bash
   python emacs_tracker_server.py --debug
   ```

2. **Use the Python API:**
   ```python
   import emacs_tracker as em
   em.start_tracking()
   # ... work in Emacs ...
   em.export_data("my_session.json")
   ```

3. **Use MCP tools:**
   - `track_user_interaction` - Single interaction capture
   - `get_tracking_log` - Retrieve recent activities
   - `export_data` - Generate session files

## 🔐 Privacy Notes

These examples use:
- **Anonymized file paths** - Generic project structure
- **Synthetic content** - No real personal data
- **Representative patterns** - Based on common workflows
- **Configurable anonymization** - Real deployments can strip sensitive info

The examples demonstrate the full capabilities while maintaining privacy and security best practices.

<!-- EOF -->