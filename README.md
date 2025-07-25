ALPT (Automatic License Plate Recognition) для распознования номерных знаков автомобилей РФ и дальнешей публикации их в MQTT

Для распознания необходимо отправить файл по http на 8000 порт. Пример успешного ответа:

```
{"result":[{"license_plate":"K777КК77","confidence":0.9688010811805725}]}
```

Также распознанные номера обводятся рамкой и сохраняются в папку uploads




Для сборки и запуска используйте:

```
docker compose up
```

Неободимые модели скачаются автоматически

Для теста используйте:

```
curl -F "file=@test.jpg" http://localhost:8000/alpr
```

Credits

- [fast-alpr](https://github.com/ankandrew/fast-alpr)
