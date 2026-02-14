"""Command-line interface for Lab2FHIR."""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .pipeline import Lab2FHIRPipeline


def main():
    """Main CLI entry point."""
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Lab2FHIR - Convert lab reports to FHIR resources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF and post to FHIR server
  lab2fhir process lab_report.pdf

  # Process and save intermediate JSON
  lab2fhir process lab_report.pdf --output-json report.json

  # Process and save FHIR bundle
  lab2fhir process lab_report.pdf --output-fhir bundle.json

  # Process without posting to server
  lab2fhir process lab_report.pdf --no-post

Environment Variables:
  OPENAI_API_KEY         - OpenAI API key (required)
  FHIR_SERVER_URL        - FHIR server URL (required for posting)
  FHIR_SERVER_AUTH_TOKEN - Optional authentication token
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process a lab report PDF"
    )
    process_parser.add_argument(
        "pdf_path", help="Path to the lab report PDF file"
    )
    process_parser.add_argument(
        "--output-json",
        "-j",
        help="Path to save intermediate JSON output",
    )
    process_parser.add_argument(
        "--output-fhir",
        "-f",
        help="Path to save FHIR bundle JSON output",
    )
    process_parser.add_argument(
        "--no-post",
        action="store_true",
        help="Do not post to FHIR server",
    )

    # Test connection command
    test_parser = subparsers.add_parser(
        "test-connection", help="Test connection to FHIR server"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "process":
            # Check if PDF exists
            pdf_path = Path(args.pdf_path)
            if not pdf_path.exists():
                print(f"Error: PDF file not found: {args.pdf_path}")
                sys.exit(1)

            # Initialize pipeline
            print("Initializing Lab2FHIR pipeline...")
            pipeline = Lab2FHIRPipeline()

            # Process the PDF
            result = pipeline.process_pdf(
                pdf_path=args.pdf_path,
                output_json_path=args.output_json,
                output_fhir_path=args.output_fhir,
                post_to_server=not args.no_post,
            )

            # Print summary
            print("\n" + "=" * 60)
            print("PROCESSING COMPLETE")
            print("=" * 60)
            print(f"PDF File: {result['pdf_file']}")
            print(f"Resources Created: {result['resource_count']}")
            print(f"Bundle ID: {result['fhir_bundle_id']}")

            if result.get("server_response"):
                if "error" in result["server_response"]:
                    print(f"\nServer Error: {result['server_response']['error']}")
                else:
                    print("\nSuccessfully posted to FHIR server!")

            print("=" * 60)

        elif args.command == "test-connection":
            print("Testing FHIR server connection...")
            pipeline = Lab2FHIRPipeline()

            if pipeline.fhir_client.test_connection():
                print(f"✓ Successfully connected to {pipeline.fhir_client.server_url}")
                sys.exit(0)
            else:
                print(f"✗ Failed to connect to {pipeline.fhir_client.server_url}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
