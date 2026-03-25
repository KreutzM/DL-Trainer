# Metadaten-Schema

## Dokument-Metadaten

Pflichtfelder:
- `doc_id`
- `product`
- `language`
- `version`
- `source_type`
- `source_file`
- `checksum`
- `import_date`
- `transform_pipeline_version`

Optionale Felder:
- `product_variant`
- `locale`
- `vendor`
- `build`
- `source_path`
- `normalized_path`
- `conversion_stage`
- `provenance`
- `notes`

## Chunk-Metadaten

Pflichtfelder:
- `chunk_id`
- `doc_id`
- `section_id`
- `title`
- `content`
- `source_spans`
- `language`
- `review_status`

## Trainings-Metadaten

Pflichtfelder:
- `id`
- `messages`
- `meta.product`
- `meta.language`
- `meta.teacher_model`
- `meta.source_doc_ids`
- `meta.review_status`
