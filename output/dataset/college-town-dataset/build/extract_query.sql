-- Source extracts for the college-town home sales dataset, version 1.0.
-- Database: PlanetScale Postgres, org `subwaymatch`, database `hasdata-data-collection`, branch `main`.
-- Source table: public.zillow_properties (36,469 rows, 154 columns, scraped 2026-03-24 to 2026-03-26).
--
-- Two queries. Export each as CSV with a header row:
--   Query 1 -> build/raw_extract.csv   one row per property        (35,822 rows)
--   Query 2 -> build/raw_events.csv    one row per history event   (284,955 rows)
-- Neither file is published: both contain property_id, the platform's ZPID.
--
-- Row filters, identical in both queries:
--   1. status IN ('SOLD','RECENTLY_SOLD')   -- excludes 609 active/pending/rental/foreclosure rows
--   2. address_undisclosed IS NOT TRUE      -- excludes 38 more rows whose address was withheld
--                                              (40 rows carry the flag; 2 already fail filter 1)
--
-- Column selection: only fields that also exist in county assessor/recorder records.
-- Deliberately NOT selected:
--   agent_name, broker_name, buyer_agent_name, buyer_broker_name, agent_phone_number,
--   broker_phone_number, agent_emails          -- named individuals and contact details
--   zestimate, rent_zestimate, rent_zestimate_url, zestimate_low_percent,
--   zestimate_high_percent, days_on_zillow     -- proprietary model output and metrics
--   url, image, photos, static_map_urls,
--   nearby, raw_json                           -- platform media and raw payloads
--   description                                -- copyrighted agent-written listing remarks
--   schools                                    -- licensed third-party school ratings
--   tax_history, and the prices in price_history -- compiled histories, not used
--
-- property_id is selected ONLY to join the two extracts and as a deterministic tie-break key.
-- The build drops it before any output file is written.
--
-- date_posted is selected but NEVER USED. Despite its name it is the date the home went on the
-- market on 84% of rows and the sale date on only 1.2%. All three published dates come from
-- query 2. See dataset_build_notes.md, section 4.


-- Query 1: properties  ->  raw_extract.csv
SELECT
    property_id,
    address_street,
    address_city,
    address_state,
    address_zipcode,
    address_county,
    county_fips,
    parcel_number,
    latitude,
    longitude,
    date_posted,
    price,
    home_type,
    beds,
    baths,
    living_area,
    lot_size,
    year_built,
    reso_stories,
    reso_basement_yn,
    reso_has_garage,
    reso_garage_parking_capacity,
    reso_has_cooling,
    reso_has_heating,
    reso_has_fireplace,
    reso_architectural_style,
    reso_roof_type,
    reso_tax_annual_amount,
    reso_tax_assessed_value,
    reso_high_school_district
FROM zillow_properties
WHERE status IN ('SOLD', 'RECENTLY_SOLD')
  AND COALESCE(address_undisclosed, false) = false
ORDER BY property_id;


-- Query 2: listing and sale history  ->  raw_events.csv
-- One row per event in price_history, oldest first within each property. Same-day events keep
-- the source's own order (the array is stored newest first, hence o DESC). Only each event's
-- date and type are extracted. Verified: the md5 of this output matches build/raw_events.csv.
SELECT z.property_id,
       (a.e->>'date')::date AS event_date,
       a.e->>'event'        AS event
FROM zillow_properties z
CROSS JOIN LATERAL jsonb_array_elements(
    CASE WHEN jsonb_typeof(z.price_history) = 'array' THEN z.price_history ELSE '[]'::jsonb END
) WITH ORDINALITY AS a(e, o)
WHERE z.status IN ('SOLD', 'RECENTLY_SOLD')
  AND COALESCE(z.address_undisclosed, false) = false
ORDER BY z.property_id, event_date, a.o DESC;
