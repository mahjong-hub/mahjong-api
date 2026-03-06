import modal

image = (
    modal.Image.debian_slim(python_version='3.12')
    .apt_install('libgl1', 'libglib2.0-0')
    .pip_install(
        'ultralytics>=8.0.0',
        'pillow',
        'fastapi[standard]',
    )
)

app = modal.App('mahjong-cv', image=image)
