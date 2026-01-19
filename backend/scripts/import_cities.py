"""Import Chinese cities from CSV file into database."""

import csv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.city import City


def import_cities(csv_path: str = "data/china-city-20250620.csv", batch_size: int = 100) -> tuple[int, int]:
    """
    Import cities from CSV file.
    
    Args:
        csv_path: Path to CSV file
        batch_size: Number of records to commit at once
        
    Returns:
        Tuple of (success_count, skip_count)
    """
    db = SessionLocal()
    success_count = 0
    skip_count = 0
    batch = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_rows = 0
            
            for row in reader:
                total_rows += 1
                
                try:
                    # Validate required fields
                    if not row.get('Location_ID') or not row.get('AD_code'):
                        print(f"⚠️  Skipping row {total_rows}: Missing required fields")
                        skip_count += 1
                        continue
                    
                    # Validate AD code (should be 6 digits)
                    ad_code = row['AD_code'].strip()
                    if not ad_code.isdigit() or len(ad_code) != 6:
                        print(f"⚠️  Skipping row {total_rows}: Invalid AD code '{ad_code}'")
                        skip_count += 1
                        continue
                    
                    # Parse coordinates
                    try:
                        latitude = float(row['Latitude']) if row.get('Latitude') else None
                        longitude = float(row['Longitude']) if row.get('Longitude') else None
                        
                        # Validate coordinate ranges
                        if latitude is not None and (latitude < -90 or latitude > 90):
                            print(f"⚠️  Warning row {total_rows}: Invalid latitude {latitude}")
                            latitude = None
                        if longitude is not None and (longitude < -180 or longitude > 180):
                            print(f"⚠️  Warning row {total_rows}: Invalid longitude {longitude}")
                            longitude = None
                    except (ValueError, TypeError):
                        latitude = None
                        longitude = None
                    
                    city = City(
                        location_id=row['Location_ID'].strip(),
                        location_name_zh=row.get('Location_Name_ZH', '').strip() or None,
                        location_name_en=row.get('Location_Name_EN', '').strip() or None,
                        ad_code=ad_code,
                        province_zh=row.get('Adm1_Name_ZH', '').strip() or None,
                        province_en=row.get('Adm1_Name_EN', '').strip() or None,
                        city_zh=row.get('Adm2_Name_ZH', '').strip() or None,
                        city_en=row.get('Adm2_Name_EN', '').strip() or None,
                        latitude=latitude,
                        longitude=longitude,
                        timezone=row.get('Timezone', '').strip() or None,
                    )
                    
                    batch.append(city)
                    
                    # Commit in batches
                    if len(batch) >= batch_size:
                        db.bulk_save_objects(batch)
                        db.commit()
                        success_count += len(batch)
                        print(f"✅ Imported {success_count}/{total_rows} cities...")
                        batch = []
                        
                except IntegrityError as e:
                    db.rollback()
                    print(f"⚠️  Skipping row {total_rows}: Duplicate entry ({str(e)[:100]})")
                    skip_count += 1
                    # Clear batch on integrity error
                    batch = []
                except Exception as e:
                    print(f"❌ Error on row {total_rows}: {e}")
                    skip_count += 1
            
            # Commit remaining batch
            if batch:
                try:
                    db.bulk_save_objects(batch)
                    db.commit()
                    success_count += len(batch)
                except IntegrityError:
                    # Try one by one for remaining batch
                    db.rollback()
                    for city in batch:
                        try:
                            db.add(city)
                            db.commit()
                            success_count += 1
                        except IntegrityError:
                            db.rollback()
                            skip_count += 1
                            
    finally:
        db.close()
    
    return success_count, skip_count


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Chinese cities from CSV')
    parser.add_argument('--csv', default='data/china-city-20250620.csv', help='Path to CSV file')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size for imports')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting import from {args.csv}...")
    print(f"📦 Batch size: {args.batch_size}")
    print()
    
    try:
        success, skipped = import_cities(args.csv, args.batch_size)
        
        print()
        print("=" * 50)
        print(f"✅ Import complete!")
        print(f"   Successful: {success}")
        print(f"   Skipped:    {skipped}")
        print(f"   Total:      {success + skipped}")
        print("=" * 50)
        
        # Verify count in database
        db = SessionLocal()
        try:
            db_count = db.query(City).count()
            print(f"📊 Total cities in database: {db_count}")
        finally:
            db.close()
            
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {args.csv}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

