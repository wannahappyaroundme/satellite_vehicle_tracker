#!/usr/bin/env python3
"""
Test script for abandoned vehicle detection system
Tests with sample_image1.pdf (2015) and sample_image2.pdf (2020)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from abandoned_vehicle_detector import AbandonedVehicleDetector
from pdf_processor import PDFProcessor
import cv2
import json


def main():
    print("=" * 80)
    print("장기 방치 차량 탐지 시스템 테스트")
    print("Abandoned Vehicle Detection System Test")
    print("=" * 80)
    print()

    # Initialize services
    print("📋 Initializing services...")
    detector = AbandonedVehicleDetector(similarity_threshold=0.90)
    pdf_processor = PDFProcessor(dpi=300)
    print("✓ Services initialized")
    print(f"  - Device: {detector.device}")
    print(f"  - Similarity threshold: {detector.similarity_threshold * 100}%")
    print()

    # Check for sample files
    pdf1_path = "sample_image1.pdf"
    pdf2_path = "sample_image2.pdf"

    if not os.path.exists(pdf1_path):
        print(f"❌ Error: {pdf1_path} not found")
        return

    if not os.path.exists(pdf2_path):
        print(f"❌ Error: {pdf2_path} not found")
        return

    print("✓ Sample files found")
    print()

    # Extract metadata
    print("📄 Extracting metadata from PDFs...")
    meta1 = pdf_processor.extract_metadata_from_pdf(pdf1_path)
    meta2 = pdf_processor.extract_metadata_from_pdf(pdf2_path)

    print(f"\n  Image 1:")
    print(f"    Year: {meta1['year']}")
    print(f"    Date: {meta1['date']}")
    print(f"    Location: {meta1['location']}")

    print(f"\n  Image 2:")
    print(f"    Year: {meta2['year']}")
    print(f"    Date: {meta2['date']}")
    print(f"    Location: {meta2['location']}")

    print(f"\n  Time difference: {meta2['year'] - meta1['year']} years")
    print()

    # Convert PDFs to images
    print("🖼️  Converting PDFs to images...")
    try:
        image1 = pdf_processor.pdf_to_image(pdf1_path)
        print(f"  ✓ Converted {pdf1_path}: {image1.shape}")

        image2 = pdf_processor.pdf_to_image(pdf2_path)
        print(f"  ✓ Converted {pdf2_path}: {image2.shape}")
    except Exception as e:
        print(f"❌ Error converting PDFs: {str(e)}")
        print("\n💡 Tip: Install poppler for pdf2image:")
        print("  macOS: brew install poppler")
        print("  Ubuntu: sudo apt-get install poppler-utils")
        return
    print()

    # Align images
    print("🔄 Aligning images...")
    try:
        image1_aligned, image2_aligned = pdf_processor.align_images(image1, image2)
        print("  ✓ Images aligned")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not align images: {str(e)}")
        print("  Continuing with original images...")
        image1_aligned, image2_aligned = image1, image2
    print()

    # Detect parking spaces
    print("🅿️  Detecting parking spaces...")
    parking_boxes = pdf_processor.detect_parking_spaces(image1_aligned, min_area=3000)
    print(f"  ✓ Detected {len(parking_boxes)} potential parking spaces")
    print()

    # Compare full images first
    print("🔍 Analyzing full image comparison...")
    full_result = detector.detect_abandoned_vehicles(
        image1_aligned,
        image2_aligned,
        meta1['year'],
        meta2['year'],
        'full_image'
    )

    print(f"\n  Full Image Analysis:")
    print(f"    Similarity: {full_result['similarity_percentage']}%")
    print(f"    Status: {full_result['status']}")
    print(f"    Risk Level: {full_result['risk_level']}")
    print(f"    Abandoned: {'YES' if full_result['is_abandoned'] else 'NO'}")
    print()

    # Compare specific regions (parking spaces)
    print("🚗 Analyzing individual parking spaces...")
    if len(parking_boxes) > 0:
        # Analyze first 5 parking spaces
        results = detector.compare_pdf_images(
            image1_aligned,
            image2_aligned,
            meta1['year'],
            meta2['year'],
            parking_boxes[:5]
        )

        print(f"  Analyzed {len(results)} parking spaces")
        print()

        # Filter abandoned vehicles
        abandoned = detector.filter_abandoned_vehicles(results)

        print(f"🚨 RESULTS:")
        print(f"  Total spaces analyzed: {len(results)}")
        print(f"  Abandoned vehicles detected: {len(abandoned)}")
        print()

        if len(abandoned) > 0:
            print("  ⚠️  Abandoned Vehicles Found (sorted by similarity):")
            for i, result in enumerate(abandoned, 1):
                print(f"\n  [{i}] {result['parking_space_id']}")
                print(f"      Similarity: {result['similarity_percentage']}%")
                print(f"      Risk Level: {result['risk_level']}")
                print(f"      Location: x={result['bbox']['x']}, y={result['bbox']['y']}")
        else:
            print("  " + "=" * 60)
            print("  ✅ 방치 차량이 발견되지 않았습니다!")
            print("  ✅ No Abandoned Vehicles Detected!")
            print("  " + "=" * 60)
            print()
            print(f"  📊 분석 결과:")
            print(f"     - 분석된 주차 공간: {len(results)}개")
            print(f"     - 탐지 임계값: {detector.similarity_threshold * 100:.0f}%")
            print(f"     - 해당 지역은 정상적으로 관리되고 있는 것으로 보입니다.")
            print()

        print()

        # Create visualization
        print("🎨 Creating visualization...")
        abandoned_boxes = [
            (r['bbox']['x'], r['bbox']['y'], r['bbox']['w'], r['bbox']['h'])
            for r in abandoned if 'bbox' in r
        ]

        visualization = pdf_processor.create_comparison_visualization(
            image1_aligned,
            image2_aligned,
            meta1['year'],
            meta2['year'],
            abandoned_boxes
        )

        output_path = "comparison_result.jpg"
        pdf_processor.save_image(visualization, output_path)
        print(f"  ✓ Visualization saved: {output_path}")
        print()

        # Save JSON results
        results_path = "detection_results.json"
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'image1': meta1,
                    'image2': meta2
                },
                'full_image_result': full_result,
                'parking_space_results': results,
                'abandoned_vehicles': abandoned
            }, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Results saved: {results_path}")

    else:
        print("  ⚠️  No parking spaces detected")

    print()
    print("=" * 80)
    print("✅ Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
