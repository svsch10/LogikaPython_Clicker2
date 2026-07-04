from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.animation import Animation    # Для ефекта анімації риби
from kivy.core.audio import SoundLoader # Для відтворення звуків
from kivy import platform

# Розмір вікна під час запуску на ПК
if platform != 'android':
    Window.size = (450, 700)

# ===== ЕКРАН ГОЛОВНОГО МЕНЮ =====
class MenuScreen(Screen):

    # Перехід до екрана гри
    def go_game(self):
        App.get_running_app().change_screen("game", "left")

    # Перехід до екрана налаштувань
    def go_settings(self):
        App.get_running_app().change_screen("settings", "left")

    # Закриття застосунку
    def exit_app(self):
        App.get_running_app().stop()

# ===== ЕКРАН ГРИ =====
class GameScreen(Screen):

    # Кількість очок гравця
    score = NumericProperty(0)

    # Номер поточного рівня
    level = NumericProperty(1)
    
    # Фоновий звук гри
    back_sound = SoundLoader.load('assets/audios/Black_Swan_part.mp3')
    back_sound.loop = True # "Закільцювати" звук
    # Звук по завершенню рівня
    level_complete_sound = SoundLoader.load('assets/audios/level_complete.ogg')

    # Викликається перед відкриттям екрана гри
    def on_pre_enter(self, *args):

        app = App.get_running_app()

        # Скидання прогресу гри
        self.score = 0
        app.LEVEL = 0
        self.level = 1

        # Ховаємо повідомлення про завершення рівня
        self.ids.level_complete.opacity = 0

        # Починаємо з першої риби
        self.ids.fish.fish_index = 0

        return super().on_pre_enter(*args)

    # Викликається після відкриття екрана гри
    def on_enter(self, *args):
        self.start_game()
        self.back_sound.volume = 0.5 # Встановлення гучності звуку
        self.back_sound.play() # Вмикаємо фоновий звук
        
        return super().on_enter(*args)

    # Запуск рівня
    def start_game(self):
        self.ids.fish.new_fish()

    # Завершення поточного рівня
    def level_complete(self, *args):
        app = App.get_running_app()

        # Показ повідомлення
        self.ids.level_complete.opacity = 1

        # Якщо існує наступний рівень
        if app.LEVEL + 1 < len(app.LEVELS):
            Clock.schedule_once(self.next_level, 2)

        # Якщо рівнів більше немає
        else:
            Clock.schedule_once(self.game_complete, 2)

        self.level_complete_sound.play() #...щоб було чутко звук завершення рівня

    # Перехід до наступного рівня
    def next_level(self, *args):
        app = App.get_running_app()

        # Збільшуємо номер рівня
        app.LEVEL += 1
        self.level = app.LEVEL + 1

        # Ховаємо напис LEVEL COMPLETE
        self.ids.level_complete.opacity = 0

        # Починаємо з першої риби нового рівня
        self.ids.fish.fish_index = 0

        self.start_game()

    # Викликається після проходження всіх рівнів
    def game_complete(self, *args):
        self.ids.level_complete.text = "YOU WIN!"
        self.ids.level_complete.opacity = 1
        Clock.schedule_once(self.go_menu, 2)

    # Повернення до меню
    def go_menu(self, *args):
        self.back_sound.stop() # Припинення фонового звуку
        App.get_running_app().change_screen("menu", "right")


# ===== ЕКРАН НАЛАШТУВАНЬ =====
class SettingsScreen(Screen):

    # Повернення до головного меню
    def go_menu(self):
        App.get_running_app().change_screen("menu", "right")

# ===== КЛАС РИБИ =====
class Fish(Image):
    # Назва поточної риби
    fish_current = None
    
    # Індекс риби в поточному рівні
    fish_index = 0
    
    # Поточна кількість XP риби
    hp_current = None
    
    # Чи рухається риба ←
    is_moving = False
    
    # Чи "росте" риба ←
    is_pulsing = False
    
    # Чи переможена риба ←
    is_defeated = False
    
    # Кут обертання риби ←
    angle = NumericProperty(0)

    # Звук по кліку на рибі
    click_music = SoundLoader.load('assets/audios/bubble01.mp3')
    
    # Звук по зникненню риби    
    defeate_music = SoundLoader.load('assets/audios/fish_def.ogg')

    # Викликається після створення віджета
    def on_kv_post(self, base_widget):
        self.base_size = self.size    # Запам'ятовуємо початковий розмір риби ←
        return super().on_kv_post(base_widget)

    # Отримання GameScreen через App
    def get_game(self):
        app = App.get_running_app()
        return app.sm.get_screen("game")

    # Створення нової риби
    def new_fish(self, *args):
        app = App.get_running_app()

        self.fish_current = app.LEVELS[app.LEVEL][self.fish_index]
        self.source = app.FISHES[self.fish_current]['source']
        self.hp_current = app.FISHES[self.fish_current]['hp']
        
        # Скидання усіх параметрів старої риби перед появою нової ←
        if not self.base_size:
            self.base_size = self.size

        self.opacity = 1
        self.angle = 0
        self.size = self.base_size
        self.is_moving = True
        self.is_pulsing = False

        game = self.get_game()

        self.x = -self.width
        self.y = game.height / 2 - self.height / 2
        
        # Анімаційний ефект з рухом риби ←
        anim_enter = Animation(
            x=game.width / 2 - self.width / 2,
            y=game.height / 2 - self.height / 2,
            duration=1.2,
            t='out_back'
        )
        
        # Сигнал про "прибуття" риби на потрібне місце ←
        def arrival(*args):
            self.is_moving = False
        
        anim_enter.bind(on_complete=arrival)
        anim_enter.start(self)

    # Приховування переможеної риби  ← (новий)
    def defeated(self):
        w, h = self.size
        cx, cy = self.center

        if self.is_defeated == True:
            return
        
        self.is_defeated = True
        
        # Анімаційний ефект з обертанням і зникненням риби
        anim = Animation(
            angle=360,                 # обертання
            size=(w * 1.8, h * 1.8),   # збільшення
            opacity=0,                 # зникнення
            center=(cx, cy),           # фіксуємо центр
            duration=0.5,
            t='out_quad'
        )

        def hide(*args):
            self.opacity = 0
            self.angle = 0
            self.size = (w, h)
            self.is_defeated = False

        anim.bind(on_complete=hide)
        anim.start(self)
        
        # Відтворення звуку програшу риби
        self.defeate_music.play()

    # Або можна зробити, щоб переможена рибка плавно зникала
    '''def defeated(self):
        anim = Animation(opacity=0, duration=0.3)
        anim.start(self)'''
    
    def pulse(self): # Збільшення/зменшення риби ←
        w, h = self.size
        cx, cy = self.center
        
        if self.is_pulsing == True:
            return
        self.is_pulsing = True
        
        anim_1 = Animation(
            size=(w * 2, h * 2),
            center=(cx, cy),
            duration=0.1,
            t='out_quad'
        )

        anim_2 = Animation(
            size=(w, h),
            center=(cx, cy),
            duration=0.1,
            t='out_quad'
        )
        
        def finish(*args):
            self.is_pulsing = False
        
        anim_click = anim_1 + anim_2
        anim_click.bind(on_complete=finish)
        anim_click.start(self)

    # Обробка кліку по рибі
    def on_touch_down(self, touch):
        app = App.get_running_app()
        game = self.get_game()
        
        # Ігноруємо клік, якщо він був поза рибою, риба рухається або вже переможена ←
        if (
            self.collide_point(*touch.pos) != True
            or self.opacity == 0
            or self.is_moving == True
            or self.is_pulsing == True
            or self.is_defeated == True
        ):
            return True
        
        self.click_music.play() # Відтворення звуку по кліку
        
        self.pulse() # Запуск збільшення/зменшення риби

        # Зменшуємо XP риби
        self.hp_current -= 1

        '''Можна зробити так, щоб риба поступово зникала, в залежності від XP
        # поточна прозорість = частка HP, що залишилась
        self.opacity = self.hp_current / app.FISHES[self.fish_current]['hp']'''

        # Додаємо очко гравцю
        game.score += 1

        # Якщо риба ще жива
        if self.hp_current > 0:
            return super().on_touch_down(touch)

        # Якщо риба переможена
        self.defeated()

        # Якщо ще є риби в рівні
        if len(app.LEVELS[app.LEVEL]) > self.fish_index + 1:
            
            # Переходимо до наступної риби
            self.fish_index += 1
            # Через 1.2 секунди створюємо її
            Clock.schedule_once(self.new_fish, 1.2)

        else:
            # Якщо риби закінчилися — завершуємо рівень
            Clock.schedule_once(game.level_complete, 1.2)
            # Скидаємо індекс для нового рівня
            self.fish_index = 0

        return super().on_touch_down(touch)


# ===== ГОЛОВНИЙ ЗАСТОСУНОК =====
class ClickerApp(App):

    # Поточний рівень гри
    LEVEL = 0

    # Дані про риб
    FISHES = {
        # Риба №1
        'fish1': {'source': 'assets/images/fish1.png', 'hp': 10},
        # Риба №2
        'fish2': {'source': 'assets/images/fish2.png', 'hp': 20}
    }

    # Список рівнів
    LEVELS = [
        ['fish1', 'fish1', 'fish2'],    # Рівень 1
        ['fish1', 'fish2', 'fish1']     # Рівень 2
    ]

    # Створення екранів застосунку
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(GameScreen(name="game"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        return self.sm

    # Зміна екрана з анімацією
    def change_screen(self, screen_name, direction):
        self.sm.transition = SlideTransition(
            direction=direction,
            duration=0.3
        )

        self.sm.current = screen_name

# ===== СТВОРЕННЯ ТА ЗАПУСК ЗАСТОСУНКУ =====
app = ClickerApp()
app.run()