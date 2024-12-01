from pathlib import Path

DB_PATH = 'sqlite:///' + str(Path(__file__).resolve().parent / 'media' / 'cinnamon.db')

IMAGES_DIR = Path('media/images')