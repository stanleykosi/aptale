# Aptale WhatsApp Formatting (Extraction Summary)

This document defines the Step 12 extraction-summary formatting used before `clarify`.

## Goals

- Keep messages concise and copy-friendly for mobile WhatsApp chat.
- Present extracted invoice fields in a predictable order.
- Provide explicit correction guidance and a single confirmation phrase.

## Extraction Summary Structure

1. `*Extraction Summary*`
   - Bullet list of key fields:
   - Invoice number
   - Invoice date
   - Route (country + port)
   - Currency
   - Total
   - Weight
   - Incoterm
2. `*Line Items*`
   - One line per item, including:
   - Description
   - Quantity + unit
   - HS code in inline code formatting
3. Optional `*Needs Confirmation*`
   - Present only when `uncertainties` is non-empty.
4. `*Next Step*`
   - Numbered instructions for:
   - Confirmation (`Confirmed`)
   - Field-path correction format
   - Practical correction examples

## WhatsApp Markdown Rules

- Use bold section headers: `*Header*`
- Use bullet and numbered lists for scanning on mobile.
- Use inline code for exact values users may copy (`hs_code`, correction paths).
- Separate major sections with a blank line.

## Clarify Hand-off

The summary message is designed to be passed directly into `clarify` so the user can:

- Reply with `Confirmed` to proceed, or
- Reply with corrections before sourcing starts.
