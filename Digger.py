from tkinter import *
import ctypes
from PIL import Image, ImageTk
import winsound

ctypes.windll.shcore.SetProcessDpiAwareness(1)

def forget_menu():
    for widget in window.winfo_children():
        widget.destroy()

def cheta():
    forget_menu()
    menu_on_screen()

selected_char_button = None
pers1_But = pers2_But = pers3_But = None
current_level_func = None

def set_selected_char(button):
    global selected_char_button
    selected_char_button = button

def start_game(level_matrix, selected_char_button, monster_delay, bg_image):
    global x, y, monster_x, monster_y, level, can_shoot, lives, traktor, monsters, bullet, crystals_collected, \
        current_monster, after_ids, c1, cell_size
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    cell_size = min(screen_width // len(level_matrix[0]), screen_height // len(level_matrix))

    level = level_matrix
    # Начальное положение персонажей
    initial_x, initial_y = 10, 5
    initial_monster_x = [15, 15, 16, 17]
    initial_monster_y = [1, 1, 1, 1]

    # Положение персонажей
    x, y = initial_x, initial_y
    monster_x = initial_monster_x.copy()
    monster_y = initial_monster_y.copy()

    # Счетчик кристаллов
    crystals_collected = 0

    # Количество жизней
    lives = 3

    # Направление движения
    dx, dy = 0, 0

    c1 = Canvas(window, width=screen_width, height=screen_height)
    c1.pack(fill="both", expand=True)
    c1.create_image(0, 0, image=bg_image, anchor='nw')

    # Загрузка изображения игрового персонажа в зависимости от выбранного в меню pers()
    if selected_char_button == pers1_But:
        image_path = 'gg/traktor.png'
    elif selected_char_button == pers2_But:
        image_path = 'gg/kopM.png'
    elif selected_char_button == pers3_But:
        image_path = 'gg/kopW.png'
    else:
        image_path = 'gg/traktor.png'

    image = Image.open(image_path)
    image = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    image_tk = ImageTk.PhotoImage(image)
    c1.image = image_tk
    traktor = c1.create_image(x * cell_size, y * cell_size, image=c1.image, anchor=NW, tags=("traktor"))

    monster_image = Image.open('gg/monstr.png')
    monster_image = monster_image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    monster_image_tk = ImageTk.PhotoImage(monster_image)
    c1.monster_image = monster_image_tk

    cristal = Image.open('gg/cristal.png')
    cristal = cristal.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    cristal_tk = ImageTk.PhotoImage(cristal)
    c1.cristal = cristal_tk

    heart_image = Image.open('gg/heart.png')
    heart_image = heart_image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
    heart_image_tk = ImageTk.PhotoImage(heart_image)
    c1.heart_image = heart_image_tk

    traktor = None
    monsters = [None, None, None, None]
    bullet = None
    can_shoot = True  # Флаг, указывающий, что можно стрелять
    after_ids = []  # Список ID отложенных вызовов

    def draw_level():
        global level, traktor, monsters, bullet
        try:
            c1.delete('obstacle')
            for i in range(len(level)):
                for j in range(len(level[i])):
                    if level[i][j] == '1':
                        c1.create_rectangle(j * cell_size, i * cell_size, j * cell_size + cell_size,
                                            i * cell_size + cell_size, fill='black',
                                            tags='obstacle')
                    elif level[i][j] == '2':
                        c1.create_image(j * cell_size, i * cell_size, image=c1.cristal, anchor=NW,
                                        tags='obstacle')

            # Отрисовка оставшихся жизней (сердец)
            heart_row = 5
            heart_col = 18
            for i in range(lives):
                c1.create_image(heart_col * cell_size, heart_row * cell_size, image=c1.heart_image,
                                anchor=W, tags='obstacle')
                heart_row -= 1

            if traktor is not None:
                c1.delete(traktor)
            traktor = c1.create_image(x * cell_size, y * cell_size, image=c1.image,
                                      anchor=NW, tags=("traktor"))
            for i in range(4):
                if monsters[i] is not None:
                    c1.delete(monsters[i])
                monsters[i] = c1.create_image(monster_x[i] * cell_size, monster_y[i] * cell_size,
                                              image=c1.monster_image, anchor=NW,
                                              tags=("monster"))
            if bullet is not None:
                c1.delete(bullet)
        except TclError:
            pass  # Если окно было закрыто, просто выходим из функции

    def move(event):
        global x, y, crystals_collected, dx, dy, level
        try:
            if event.keysym == 'Right' and x < len(level[0]) - 2:
                dx, dy = 1, 0
                if selected_char_button == pers1_But:
                    image = Image.open('gg/traktor.png')
                elif selected_char_button == pers2_But:
                    image = Image.open('gg/kopM.png')
                elif selected_char_button == pers3_But:
                    image = Image.open('gg/kopW.png')
                else:
                    image = Image.open('gg/traktor.png')
                image = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
                image_tk = ImageTk.PhotoImage(image)
                c1.image = image_tk
                c1.itemconfig(traktor, image=c1.image)
            elif event.keysym == 'Left' and x > 1:
                dx, dy = -1, 0
                if selected_char_button == pers1_But:
                    image = Image.open('gg/traktor.png')
                elif selected_char_button == pers2_But:
                    image = Image.open('gg/kopM.png')
                elif selected_char_button == pers3_But:
                    image = Image.open('gg/kopW.png')
                else:
                    image = Image.open('gg/traktor.png')
                image = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image_tk = ImageTk.PhotoImage(image)
                c1.image = image_tk
                c1.itemconfig(traktor, image=c1.image)
            elif event.keysym == 'Up' and y > 1:
                dx, dy = 0, -1
            elif event.keysym == 'Down' and y < len(level) - 2:
                dy, dx = 1, 0
            else:
                return

            # Копание
            if level[y + dy][x + dx] == '0':
                level[y + dy][x + dx] = '1'
                x += dx
                y += dy
            elif level[y + dy][x + dx] == '1':
                x += dx
                y += dy
            elif level[y + dy][x + dx] == '2':  # Если на пути кристалл
                level[y + dy][x + dx] = '1'  # Удаляем кристалл
                x += dx
                y += dy
                crystals_collected += 1  # Увеличиваем счетчик кристаллов
                if crystals_collected >= 10:  # Если собрано 10 кристаллов
                    lavel()  # Закрываем окно
            draw_level()
        except TclError:
            pass  # Если окно было закрыто, просто выходим из функции

    def draw_bullet(bullet_x, bullet_y):
        global bullet
        if bullet is not None and c1 is not None:
            c1.delete(bullet)
        bullet = c1.create_oval(bullet_x * cell_size + cell_size // 2, bullet_y * cell_size + cell_size //
                                2,bullet_x * cell_size + cell_size // 2 + cell_size // 4, bullet_y *
                                cell_size + cell_size // 2 + cell_size // 4, fill='red', tags='bullet')

    def move_bullet(bullet_x, bullet_y, dx, dy):
        global bullet, monsters, level, after_ids
        try:
            if 0 <= bullet_x < len(level[0]) and 0 <= bullet_y < len(level) and level[bullet_y][bullet_x] == '1':
                # Проверяем все монстров на пути пули
                for i in range(4):
                    if monster_x[i] != -1 and monster_y[i] != -1:
                        if bullet_x == monster_x[i] and bullet_y == monster_y[i]:
                            level[bullet_y][bullet_x] = '1'
                            monster_x[i], monster_y[i] = -1, -1
                            draw_level()
                            if c1 is not None:
                                c1.delete('bullet')
                            bullet = None
                            return

                if c1 is not None:
                    draw_bullet(bullet_x, bullet_y)
                bullet_x += dx
                bullet_y += dy
                after_id = c1.after(50, move_bullet, bullet_x, bullet_y, dx, dy)
                after_ids.append(after_id)
            else:
                if c1 is not None:
                    c1.delete('bullet')
                bullet = None
        except TclError:
            pass  # Если окно было закрыто, просто выходим из функции

    def shoot(event):
        global bullet, x, y, dx, dy, can_shoot, after_ids
        if event.keysym == 'Return' and can_shoot and c1 is not None:
            can_shoot = False  # Блокируем выстрел
            draw_bullet(x, y)
            move_bullet(x + dx, y + dy, dx, dy)
            after_id = window.after(5000, reset_shoot)  # Устанавливаем задержку выстрела 5000 миллисекунд
            after_ids.append(after_id)

    def reset_shoot():
        global can_shoot
        can_shoot = True  # Разрешаем выстрел после задержки

    current_monster = 0

    def spawn_monsters():
        global current_monster, after_ids
        try:
            move_monster(current_monster)
            current_monster += 1
            if current_monster < 4:
                after_id = c1.after(600, spawn_monsters)
                after_ids.append(after_id)
        except TclError:
            pass

    def move_monster(monster_index):
        global monster_x, monster_y, x, y, lives
        try:
            # Находим кратчайший путь от монстра до трактораВ
            path = find_shortest_path(monster_x[monster_index], monster_y[monster_index], x, y)

            if path:
                # Делаем шаг по найденному пути
                next_x, next_y = path[0]
                monster_x[monster_index] = next_x
                monster_y[monster_index] = next_y

                # Проверяем соприкосновение монстра с трактором
                if next_x == x and next_y == y:
                    lives -= 1  # Уменьшаем количество жизней
                    if lives == 0:  # Если жизней не осталось
                        game_over(current_level_func)  # Завершаем игру
                    else:
                        # Удаляем одно изображение сердца из матрицы
                        for i in range(len(level)):
                            for j in range(len(level[i])):
                                if level[i][j] == '3':
                                    level[i][j] = '0'
                                    break

                        # Восстанавливаем начальные позиции персонажа и монстров
                        x, y = initial_x, initial_y
                        monster_x = initial_monster_x.copy()
                        monster_y = initial_monster_y.copy()

            draw_level()
            c1.after(monster_delay, move_monster, monster_index)  # Вызываем move_monster() с задержкой
        except TclError:
            pass

    def find_shortest_path(start_x, start_y, target_x, target_y):
        queue = [(start_x, start_y, [])]  # Очередь с начальной координатой и пустым путем
        visited = set()  # Множество посещенных координат

        while queue:
            x, y, path = queue.pop(0)  # Извлекаем координаты и путь из очереди

            # Если достигли цели, возвращаем путь
            if x == target_x and y == target_y:
                return path

            # Пропускаем посещенные координаты и непроходимые ячейки
            if (x, y) in visited or y < 0 or y >= len(level) or x < 0 or x >= len(level[0]) or level[y][x] != '1':
                continue

            visited.add((x, y))  # Добавляем координаты в множество посещенных

            # Добавляем в очередь соседние проходимые ячейки с новым путем
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(level[0]) and 0 <= new_y < len(level) and level[new_y][new_x] == '1':
                    new_path = path + [(new_x, new_y)]
                    queue.append((new_x, new_y, new_path))

        # Если путь не найден, возвращаем None
        return None

    window.bind('<Right>', move)
    window.bind('<Left>', move)
    window.bind('<Up>', move)
    window.bind('<Down>', move)
    window.bind('<Return>', shoot)

    window.after(1000,  spawn_monsters)
    window.mainloop()
def lavel1():
    global current_level_func
    current_level_func = lavel1
    level_matrix = [
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '1', '0'],
        ['0', '0', '0', '0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0'],
        ['0', '0', '2', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0'],
        ['0', '0', '2', '2', '0', '0', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1', '0', '0', '3'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '2', '0', '0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '2', '0', '0', '0', '2', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    ]
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    bg_image = ImageTk.PhotoImage(
        Image.open('gg/ground1.png').resize((screen_width, screen_height), Image.Resampling.LANCZOS))
    start_game(level_matrix, selected_char_button, monster_delay=190, bg_image=bg_image)
    window.mainloop()

def lavel2():
    global current_level_func
    current_level_func = lavel2
    level_matrix = [
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '0'],
        ['0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '2', '0', '0'],
        ['0', '0', '2', '2', '0', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '2', '0', '0'],
        ['0', '0', '2', '2', '0', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '0', '0', '0', '3'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '2', '2', '0', '0', '0', '0', '0', '0', '2', '2', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    ]
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    bg_image = ImageTk.PhotoImage(
        Image.open('gg/ground2.png').resize((screen_width, screen_height), Image.Resampling.LANCZOS))
    start_game(level_matrix, selected_char_button, monster_delay=150, bg_image=bg_image)
    window.mainloop()
def lavel3():
    global current_level_func
    current_level_func = lavel3
    level_matrix = [
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '2', '2', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1', '0'],
        ['0', '0', '0', '0', '0', '0', '2', '0', '0', '0', '1', '0', '0', '0', '1', '2', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '1', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '1', '1', '1', '1', '1', '1', '1', '0', '0', '0', '3'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '2', '0', '0'],
        ['0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '2', '0', '0'],
        ['0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1', '0', '0', '0', '0'],
        ['0', '0', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '2', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
        ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
    ]
    screen_width, screen_height = window.winfo_screenwidth(), window.winfo_screenheight()
    bg_image = ImageTk.PhotoImage(
        Image.open('gg/ground3.png').resize((screen_width, screen_height), Image.Resampling.LANCZOS))
    start_game(level_matrix, selected_char_button, monster_delay=115, bg_image=bg_image)
    window.mainloop()

def game_over(level_func):
    forget_menu()
    bg_over = ImageTk.PhotoImage(Image.open('gg/gameover.png').resize((w, h)))
    label = Label(window, image=bg_over)
    label.place(relx=.5, rely=.5, anchor='c')

    perez = ImageTk.PhotoImage(Image.open('button/retry.png').resize((round(w*.2083), round(h*.3333))))
    pere = Button(image=perez, command=level_func)
    pere.place(relx=.3, rely=.65, anchor="c")

    verl = ImageTk.PhotoImage(Image.open('button/backlvl.png').resize((round(w*.2083), round(h*.3333))))
    verll = Button(command=lavel, image=verl)
    verll.place(relx=.7, rely=.65, anchor="c")
    window.mainloop()
def lavel(): #окно с выбором уровня игры
    forget_menu()
    bg1 = ImageTk.PhotoImage(Image.open('gg/lvlfon.png').resize((w, h)))
    label = Label(window, image=bg1)
    label.place(relx=.5, rely=.5, anchor='c')

    lvl11 = ImageTk.PhotoImage(Image.open('button/l1.png').resize((round(w * .0786), round(h * .1258))))
    lvl1 = Button(command=lavel1, image=lvl11)
    lvl1.place(relx=.25, rely=.6, anchor="c")

    lvl22 = ImageTk.PhotoImage(Image.open('button/l2.png').resize((round(w * .0786), round(h * .1258))))
    lvl2 = Button(command=lavel2, image=lvl22)
    lvl2.place(relx=.5, rely=.6, anchor="c")

    lvl33 = ImageTk.PhotoImage(Image.open('button/l3.png').resize((round(w * .0786), round(h * .1258))))
    lvl3 = Button(command=lavel3, image=lvl33)
    lvl3.place(relx=.75, rely=.6, anchor="c")

    men = ImageTk.PhotoImage(Image.open('button/back.png').resize((round(w * .2443), round(h * .0917))))
    gl_menu = Button(command=cheta, image=men)
    gl_menu.place(relx=.67, rely=.83, anchor="c")
    window.mainloop()

def sit(): #меню управления
    bg1 = ImageTk.PhotoImage(Image.open('gg/uprfon.png').resize((w, h)))
    label = Label(window, image=bg1)
    label.place(relx=.5, rely=.5, anchor='c')

    men = ImageTk.PhotoImage(Image.open('button/back.png').resize((round(w * .2443), round(h * .0917))))
    gl_menu = Button(command=cheta, image=men)
    gl_menu.place(relx=.70, rely=.83, anchor="c")
    window.mainloop()

def pers(): #меню выбора персонажа
    bg1 = ImageTk.PhotoImage(Image.open('gg/persfon.png').resize((w, h)))
    label = Label(window, image=bg1)
    label.place(relx=.5, rely=.5, anchor='c')

    pers1tr = ImageTk.PhotoImage(Image.open('Button/Pers1.png').resize((round(w * .1563), round(h * .25))))
    pers2m = ImageTk.PhotoImage(Image.open('Button/Pers2.png').resize((round(w * .1563), round(h * .25))))
    pers3w = ImageTk.PhotoImage(Image.open('Button/Pers3.png').resize((round(w * .1563), round(h * .25))))

    global pers1_But, pers2_But, pers3_But
    pers1_But = Button(command=lambda: set_selected_char(pers1_But), image=pers1tr)
    pers1_But.place(relx=.3, rely=.6, anchor="c")
    pers2_But = Button(command=lambda: set_selected_char(pers2_But), image=pers2m)
    pers2_But.place(relx=.5, rely=.6, anchor="c")
    pers3_But = Button(command=lambda: set_selected_char(pers3_But), image=pers3w)
    pers3_But.place(relx=.7, rely=.6, anchor="c")

    men = ImageTk.PhotoImage(Image.open('button/back.png').resize((round(w * .2443), round(h * .0917))))
    gl_menu = Button(command=cheta, image=men)
    gl_menu.place(relx=.7, rely=.83, anchor="c")
    window.mainloop()


def toggle_music(button): #функция для включения/выключения музыки
    global music_playing
    if music_playing.get():
        winsound.PlaySound(None, winsound.SND_PURGE)
        button.config(image=sound_off)
        music_playing.set(False)
    else:
        winsound.PlaySound("gg/Garoad.wav", winsound.SND_ASYNC | winsound.SND_LOOP)
        button.config(image=sound_on)
        music_playing.set(True)


def menu_on_screen(): #главное меню
    global button4
    forget_menu()
    bg = ImageTk.PhotoImage(Image.open('gg/menu.png').resize((w, h)))
    label = Label(window, image=bg)
    label.place(relx=.5, rely=.5, anchor='c')

    ex = ImageTk.PhotoImage(Image.open('button/exit.png').resize((round(w * .2479), round(h * .0633))))
    button1 = Button(command=window.destroy, image=ex)
    button1.place(relx=.5, rely=.85, anchor="c")

    yp = ImageTk.PhotoImage(Image.open('button/control.png').resize((round(w * .2479), round(h * .0633))))
    button2 = Button(command=sit, image=yp)
    button2.place(relx=.5, rely=.75, anchor="c")

    per = ImageTk.PhotoImage(Image.open('button/choicepers.png').resize((round(w * .2479), round(h * .0633))))
    button3 = Button(command=pers, image=per)
    button3.place(relx=.5, rely=.65, anchor="c")

    button4 = Button(command=lambda: toggle_music(button4))
    button4.place(relx=.85, rely=.85, anchor="c")

    pl = ImageTk.PhotoImage(Image.open('button/play.png').resize((round(w * .2479), round(h * .0633))))
    button5 = Button(command=lavel, image=pl)
    button5.place(relx=.5, rely=.55, anchor="c")

    if music_playing.get():
        button4.config(image=sound_on)
    else:
        button4.config(image=sound_off)

    window.mainloop()

window = Tk()
w, h = window.winfo_screenwidth(), window.winfo_screenheight()
window.title("DIGGER")
window.attributes('-fullscreen', True)

sound_on = ImageTk.PhotoImage(Image.open('button/song_on.png').resize((round(w * .0396), round(h * .0633))))
sound_off = ImageTk.PhotoImage(Image.open('button/song_off.png').resize((round(w * .0396), round(h * .0633))))

music_playing = BooleanVar()
music_playing.set(False)

menu_on_screen()