# Story Generation Deep Dive

## Overview
This module covers Odibi's automatic documentation system that transforms pipeline execution into rich, shareable stories in multiple formats.

## Learning Objectives
- Understand StoryGenerator architecture and markdown generation
- Track detailed execution metrics with NodeExecutionMetadata
- Aggregate pipeline data with PipelineStoryMetadata
- Use multi-format renderers (Markdown, HTML, JSON)
- Customize themes and branding
- Analyze story content patterns
- Test and validate story generation

## Files
- **lesson.ipynb** - Main teaching content
- **exercises.ipynb** - Practice problems
- **solutions.ipynb** - Exercise solutions

## Key Concepts

### 1. StoryGenerator
Creates markdown documentation from pipeline execution:
```python
generator = StoryGenerator(
    pipeline_name="data_pipeline",
    max_sample_rows=10,
    output_path="stories/"
)

story_path = generator.generate(
    node_results=results,
    completed=["node1", "node2"],
    failed=[],
    skipped=[],
    duration=12.5,
    start_time="2024-01-15T10:00:00",
    end_time="2024-01-15T10:00:12"
)
```

### 2. NodeExecutionMetadata
Tracks detailed node-level metrics:
- Row counts (in/out/change/percentage)
- Schema evolution (added/removed columns)
- Performance timing
- Error details

### 3. PipelineStoryMetadata
Aggregates pipeline-level information:
- Overall status and success rates
- Total rows processed
- Project/plant/business context
- Theme preferences

### 4. Multi-Format Renderers
- **MarkdownStoryRenderer** - Human-readable GitHub-flavored markdown
- **HTMLStoryRenderer** - Professional interactive reports
- **JSONStoryRenderer** - Machine-readable API format

### 5. Theme System
Customizable branding with built-in themes:
- Default
- Corporate
- Dark
- Minimal

## Exercises

1. **Build Custom CSV Renderer** - Export stories as CSV format
2. **Add Memory Tracking** - Extend metadata with memory metrics
3. **Create HTML Theme** - Build organization-specific theme
4. **Implement Story Diff** - Compare two pipeline runs
5. **Story Analytics Dashboard** - Analyze multiple story files

## Prerequisites
- Understanding of Odibi node execution
- Familiarity with dataclasses
- Basic knowledge of Markdown/HTML/JSON formats

## Next Steps
After completing this module, you'll be able to:
- Generate automatic documentation for pipeline runs
- Track data lineage and transformations
- Create branded reports for stakeholders
- Analyze pipeline performance trends
- Build custom renderers for specific needs
