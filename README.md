# Ruletka
Задание Псевдорулетка 
Есть псевдорулетка с джекпотом, которая состоит из 11 ячеек:
●	числа от 1 до 10
●	ячейка джекпот

Пользователь крутит рулетку и ему выпадает одна из ячеек. После того, как ячейка выпала, она исключается из дальнейшего выпадения (т.е. в этом раунде рулетки она уже выпасть не может). Ячейка джекпот выпадает только после того как выпали все ячейки от 1 до 10. После того, как выпадает джекпот, раунд рулетки завершается и начинается новый раунд. Шанс выпадения каждой ячейки одинаковый.

Дополнительно, по желанию, можно реализовать рандом на основе таблицы весов вероятности выпадения каждой ячейки, указанной ниже (но это требование не обязательно):

Ячейка	Вес
1	20
2	100
3	45
4	70
5	15
6	140
7	20
8	20
9	140
10	45

Необходимо написать веб-приложение, которое крутит рулетку согласно указанной логике и согласно указанным весам. Для сохранения состояния раунда рулетки необходимо использовать БД. Также должен сохранятся в другой таблице лог выпадений ячеек.



Способ прокручивания рулетки - POST HTTP запрос с JSON данными.
Дополнительно нужно реализовать функционал получения статистической информации (GET HTTP запрос с JSON ответом):
●	Какое количество людей участвовало в рулетке (таблица, где в строке первый элемент это номер раунда рулетки, второй элемент количество пользователей)
●	Список самых активных пользователей, где для каждого элемента нужно указать:
○	айди пользователя
○	количество раундов рулетке в которые он участвовал
○	среднее количество прокручиваний рулетки за раунд
Ограничения:
●	Механизм выбора ячейки на основании весов ячейки необходимо реализовать самостоятельно без использования сторонних библиотек
●	Соблюдение современных паттернов, принципов и стандартов разработки
●	Соблюдение гайдлайнов
●	БД можно использовать MySQL или Postgres последних стабильных версий

Реализацию необходимо залить на любой публичный\приватный git репозиторий. 

Будет большим плюсом, если упакуете проект в docker-compose проект или docker образ.
