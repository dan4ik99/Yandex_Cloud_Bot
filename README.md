# Yandex_Cloud_Bot
Шуточный Telegram-bot на основе Multi-armed bandit для сбора обратной связи о предпочитаемых квартирах (по фотографиям)


Идея: показывать пользователям фотографии "странных" квартир и спрашивать, выбрали бы они такую квартиру для проживания. При этом оговаривается условие, что "нормальные" квартиры пропали с рынка и остались только квартиры с рядом недостатков. Пользователю предстоит выбирать из двух предложенных вариантов ответов 'да' или 'нет' (то есть за раз пользователю показывается одна картинка).

Немного про многоруких бандитов:
1) https://towardsdatascience.com/solving-the-multi-armed-bandit-problem-b72de40db97c
2) https://habr.com/ru/company/avito/blog/417571/

Идея использования алгоритма многоруких бандитов в чат боте состоит в том, что пользователю показывается определенная категория картинок на основе его предыдущих ответов. Есть две категории картинок. Показываемые категории картинок выбираются с помощью алгоритма, а картинки внутри категорий выбираются с помощью генератора случайных чисел. 

**Немного об используемом алгоритме**
Статья на Хабре: https://habr.com/ru/post/425619/

Агенты – алгоритмы, которые ищут подход к выбору решений в реальном времени, чтобы достичь баланс между исследованием пространства вариантов и использованием самого оптимального варианта. Этот баланс очень важен. Пространство вариантов надо исследовать, чтобы иметь понятие о том, какой вариант самый лучший. Если мы сначала обнаружили этот самый оптимальный вариант, а потом все время его используем – мы максимизируем суммарную награду, которая нам доступна из окружающей среды. С другой стороны, мы также хотим исследовать другие возможные варианты – вдруг они в будущем окажутся лучше, а мы просто этого пока не знаем? Иными словами, мы хотим застраховаться против возможных убытков, пробуя немного экспериментировать с субоптимальными вариантами, чтобы уточнить для себя их окупаемость. Если их окупаемость на самом деле более высокая, их можно показывать чаще. Другой плюс от исследования вариантов в том, что мы можем лучше понять не только среднюю окупаемость, но и то, как примерно окупаемость распределяется, т.е мы можем лучше оценить неопределенность.
Главная проблема, следовательно, это решить – как лучше всего выйти из дилеммы между исследованием и использованием (exploration-exploitation tradeoff).


**Эпсилон-жадный алгоритм (epsilon-greedy algorithm). Как раз его и использую**

Типичный способ выйти из этой дилеммы – эпсилон-жадный алгоритм. «Жадный» означает именно то, о чем вы подумали. После некого начального периода, когда мы случайно делаем попытки – скажем, 1000 раз, алгоритм жадно выбирает самый лучший вариант k в e процентах попыток. Например, если e=0.05, алгоритм 95% времени выбирает лучший вариант, а в оставшиеся 5% времени выбирает случайные попытки. На самом деле, это довольно эффективный алгоритм, однако он может недостаточно исследовать пространство вариантов, и следовательно, недостаточно хорошо оценить, какой вариант самый лучший, застрять на субоптимальном варианте. Давайте покажем в коде, как этот алгоритм работает.

Но сначала некоторые зависимости. Мы должны определить окружающую среду Environment. Это контекст, в котором алгоритмы будут запускаться. В данном случае, контекст очень простой. Он вызывает агента, чтобы агент решил, какое выбрать действие, дальше контекст запускает это действие и возвращает полученные за него очки обратно агенту (который как-то обновляет свое состояние).

Суть эпсилон-жадного алгоритма такова.

* Случайным образом выбрать k для n попыток.
* На каждой попытке для каждого варианта оценить выигрыш.
* После всех n попыток:
* С вероятностью 1-e выбрать k с самым высоким выигрышем;
* С вероятностью e выбрать K случайно.
