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
- `product`
- `language`
- `source_path`
- `normalized_path`
- `chunk_path`
- `section_id`
- `section_title`
- `section_path`
- `chunk_index`
- `chunk_count_in_doc`
- `char_count`
- `conversion_stage`
- `provenance`
- `title`
- `content`
- `source_spans`
- `review_status`

Sinnvolle Zusatzfelder:
- `heading_level`
- `chunk_index_in_section`
- `section_chunk_count`
- `contains_list`
- `contains_steps`
- `contains_source_marker`
- `summary`

## Trainings-Metadaten

Pflichtfelder:
- `id`
- `messages`
- `meta.product`
- `meta.language`
- `meta.teacher_model`
- `meta.source_doc_ids`
- `meta.review_status`
