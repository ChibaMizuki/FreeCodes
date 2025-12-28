import cv2

# カメラを起動（通常は0。外部カメラを使う場合は1や2）
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラが見つかりませんでした。")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("フレームを取得できませんでした。")
        break

    cv2.imshow("Web camera test", frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
