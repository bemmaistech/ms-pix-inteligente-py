import cv2
import numpy as np
from Controller.controlador import Controlador
from pathlib import Path


def main():
    img_path = Path('tmp_test.png')

    # create a simple image with text using OpenCV
    img = np.full((200, 800, 3), 255, dtype=np.uint8)
    cv2.putText(img, 'Teste 123', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.imwrite(str(img_path), img)

    try:
        c = Controlador(str(img_path))
        ok = c.processar_fluxo()
        print({'result': ok})
    except Exception as e:
        print({'error': type(e).__name__, 'message': str(e)})
    finally:
        if img_path.exists():
            img_path.unlink()


if __name__ == '__main__':
    main()
