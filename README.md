# Yandex_Cloud_Bot
Шуточный Telegram-bot на основе Multi-armed bandit для сбора обратной связи о предпочитаемых квартирах (по фотографиям)


Идея: показывать пользователям фотографии "странных" квартир и спрашивать, выбрали бы они такую квартиру для проживания. При этом оговаривается условие, что "нормальные" квартиры пропали с рынка и остались только квартиры с рядом недостатков. Пользователю предстоит выбирать из двух предложенных вариантов ответов 'да' или 'нет' (то есть за раз пользователю показывается одна картинка).

Всего у нас две категории "странных" квартир. В первой категории находятся квартиры с 'излишками' в ремонте. Во второй категории находятся квартиры с 'нехваткой' ремонта. Для наглядности:

Категория 1 (кодовое название - 'избыток')                                            
![image](https://user-images.githubusercontent.com/47105722/228045585-f893bf4a-4a70-4094-9c34-489e5805cbb3.png

Категория 2 (кодовое название - 'недостаток')
![image](https://user-images.githubusercontent.com/47105722/228045670-7d3e47a0-2fdf-49e1-bec2-50218e223e0f.png)

