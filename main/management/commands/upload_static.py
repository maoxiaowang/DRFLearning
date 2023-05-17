from pathlib import Path

from django.core.management import BaseCommand

from common.core.storage import makeup_s3_url, get_s3_bucket

s3_bucket = get_s3_bucket()


class Command(BaseCommand):

    def _list_files(self, path: Path):
        if path.is_dir():
            for sub_path in path.iterdir():
                yield from self._list_files(sub_path)
        elif path.is_file():
            yield path

    def handle(self, *args, **options):
        for path in Path('static').iterdir():
            files = self._list_files(path)
            for fp in files:
                with open(fp, 'rb') as f:
                    try:
                        obj = s3_bucket.put_object(Key=str(fp), Body=f)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR('[ FAILED ] ') + f'{str(fp)} uploading failed: {str(e)}')
                        continue
                    url = makeup_s3_url(obj.key)
                    self.stdout.write(self.style.SUCCESS('[   OK   ] ') + f'{str(fp)} -> {url}')
