from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime, timedelta
import json
import os

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            self.bg_color = Color(0.2, 0.6, 1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class ShiftCalendarApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = datetime.now()
        self.shifts = {}
        self.food_expenses = {}  # {date: amount}
        self.hourly_rate = 500
        self.load_data()

    def build(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.main_layout.canvas.before.clear()
        
        with self.main_layout.canvas.before:
            Color(0.95, 0.95, 0.97, 1)  # iOS светлый фон
            self.bg_rect = RoundedRectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        
        self.main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # Заголовок
        header = BoxLayout(size_hint_y=0.08, spacing=10)
        
        prev_btn = Button(
            text='‹',
            font_size='32sp',
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.2, 0.6, 1, 1),
            size_hint_x=0.15
        )
        prev_btn.bind(on_press=self.prev_month)
        
        self.month_label = Label(
            text='',
            font_size='22sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_x=0.7
        )
        
        next_btn = Button(
            text='›',
            font_size='32sp',
            background_normal='',
            background_color=(1, 1, 1, 1),
            color=(0.2, 0.6, 1, 1),
            size_hint_x=0.15
        )
        next_btn.bind(on_press=self.next_month)
        
        header.add_widget(prev_btn)
        header.add_widget(self.month_label)
        header.add_widget(next_btn)
        
        # Дни недели
        weekdays_box = BoxLayout(size_hint_y=0.05, spacing=2)
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day in days:
            lbl = Label(
                text=day,
                color=(0.5, 0.5, 0.5, 1),
                font_size='13sp',
                bold=True
            )
            weekdays_box.add_widget(lbl)
        
        # Календарь
        scroll = ScrollView(size_hint=(1, 0.45))
        self.calendar_grid = GridLayout(cols=7, spacing=3, size_hint_y=None, padding=5)
        self.calendar_grid.bind(minimum_height=self.calendar_grid.setter('height'))
        scroll.add_widget(self.calendar_grid)
        
        # Статистика
        stats_box = BoxLayout(orientation='vertical', size_hint_y=0.28, padding=10, spacing=8)
        
        with stats_box.canvas.before:
            Color(1, 1, 1, 1)
            self.stats_bg = RoundedRectangle(pos=stats_box.pos, size=stats_box.size, radius=[20])
        
        stats_box.bind(pos=lambda *args: setattr(self.stats_bg, 'pos', stats_box.pos),
                      size=lambda *args: setattr(self.stats_bg, 'size', stats_box.size))
        
        self.stats_label = Label(
            text='',
            color=(0.1, 0.1, 0.1, 1),
            font_size='15sp',
            halign='left',
            valign='top',
            markup=True
        )
        self.stats_label.bind(size=self.stats_label.setter('text_size'))
        stats_box.add_widget(self.stats_label)
        
        # Кнопки
        buttons_layout = BoxLayout(size_hint_y=0.14, spacing=10)
        
        settings_btn = Button(
            text='⚙ Настройки',
            font_size='16sp',
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1)
        )
        settings_btn.bind(on_press=self.show_settings)
        
        food_btn = Button(
            text='🍽 Питание',
            font_size='16sp',
            background_normal='',
            background_color=(1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        food_btn.bind(on_press=self.show_food_menu)
        
        buttons_layout.add_widget(settings_btn)
        buttons_layout.add_widget(food_btn)
        
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(weekdays_box)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(stats_box)
        self.main_layout.add_widget(buttons_layout)
        
        self.update_calendar()
        return self.main_layout
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.main_layout.pos
        self.bg_rect.size = self.main_layout.size

    def update_calendar(self):
        self.calendar_grid.clear_widgets()
        self.month_label.text = self.current_date.strftime('%B %Y')
        
        first_day = datetime(self.current_date.year, self.current_date.month, 1)
        start_weekday = first_day.weekday()
        
        # Пустые ячейки
        for _ in range(start_weekday):
            self.calendar_grid.add_widget(Label(text=''))
        
        # Дни месяца
        if self.current_date.month == 12:
            days_in_month = 31
        else:
            next_month = datetime(self.current_date.year, self.current_date.month + 1, 1)
            days_in_month = (next_month - timedelta(days=1)).day
        
        for day in range(1, days_in_month + 1):
            date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
            
            day_box = BoxLayout(orientation='vertical', size_hint_y=None, height=70)
            
            btn = Button(
                text=str(day),
                font_size='16sp',
                background_normal='',
                bold=True
            )
            
            # Определяем цвет
            if date_str in self.shifts:
                if self.shifts[date_str]['type'] == 'work':
                    btn.background_color = (0.2, 0.8, 0.4, 1)  # зеленый
                    btn.color = (1, 1, 1, 1)
                else:
                    btn.background_color = (1, 0.3, 0.3, 1)  # красный
                    btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (1, 1, 1, 1)
                btn.color = (0.1, 0.1, 0.1, 1)
            
            # Индикатор питания
            food_indicator = Label(
                text='🍽' if date_str in self.food_expenses else '',
                size_hint_y=0.3,
                font_size='10sp'
            )
            
            btn.bind(on_press=lambda x, d=date_str: self.day_clicked(d))
            
            day_box.add_widget(btn)
            day_box.add_widget(food_indicator)
            
            self.calendar_grid.add_widget(day_box)
        
        self.update_stats()

    def day_clicked(self, date_str):
        content = BoxLayout(orientation='vertical', spacing=12, padding=15)
        
        content.add_widget(Label(
            text=f'📅 {date_str}',
            size_hint_y=0.15,
            font_size='18sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        ))
        
        # Часы работы
        hours_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        hours_layout.add_widget(Label(text='⏱ Часов:', color=(0.1, 0.1, 0.1, 1)))
        hours_input = TextInput(
            text=str(self.shifts.get(date_str, {}).get('hours', 8)),
            multiline=False,
            input_filter='int',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        hours_layout.add_widget(hours_input)
        content.add_widget(hours_layout)
        
        # Питание
        food_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        food_layout.add_widget(Label(text='🍽 Питание:', color=(0.1, 0.1, 0.1, 1)))
        food_input = TextInput(
            text=str(self.food_expenses.get(date_str, 0)),
            multiline=False,
            input_filter='int',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        food_layout.add_widget(food_input)
        content.add_widget(food_layout)
        
        # Кнопки
        work_btn = Button(
            text='✓ Рабочая смена',
            size_hint_y=0.18,
            background_normal='',
            background_color=(0.2, 0.8, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        
        off_btn = Button(
            text='✗ Выходной',
            size_hint_y=0.18,
            background_normal='',
            background_color=(1, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        
        clear_btn = Button(
            text='⌫ Очистить',
            size_hint_y=0.18,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        
        content.add_widget(work_btn)
        content.add_widget(off_btn)
        content.add_widget(clear_btn)
        
        popup = Popup(
            title='Настройка дня',
            content=content,
            size_hint=(0.85, 0.65),
            background_color=(1, 1, 1, 1)
        )
        
        def set_work(instance):
            hours = int(hours_input.text) if hours_input.text else 8
            self.shifts[date_str] = {'type': 'work', 'hours': hours}
            
            food_amount = int(food_input.text) if food_input.text else 0
            if food_amount > 0:
                self.food_expenses[date_str] = food_amount
            elif date_str in self.food_expenses:
                del self.food_expenses[date_str]
            
            self.save_data()
            self.update_calendar()
            popup.dismiss()
        
        def set_off(instance):
            self.shifts[date_str] = {'type': 'off', 'hours': 0}
            
            food_amount = int(food_input.text) if food_input.text else 0
            if food_amount > 0:
                self.food_expenses[date_str] = food_amount
            elif date_str in self.food_expenses:
                del self.food_expenses[date_str]
            
            self.save_data()
            self.update_calendar()
            popup.dismiss()
        
        def clear_day(instance):
            if date_str in self.shifts:
                del self.shifts[date_str]
            if date_str in self.food_expenses:
                del self.food_expenses[date_str]
            self.save_data()
            self.update_calendar()
            popup.dismiss()
        
        work_btn.bind(on_press=set_work)
        off_btn.bind(on_press=set_off)
        clear_btn.bind(on_press=clear_day)
        
        popup.open()

    def update_stats(self):
        total_shifts = 0
        total_hours = 0
        total_food = 0
        total_food_deduction = 0
        
        for date_str, data in self.shifts.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month and
                data['type'] == 'work'):
                total_shifts += 1
                total_hours += data['hours']
        
        # Питание - вычитаем превышение 500₽ с каждого дня
        for date_str, amount in self.food_expenses.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month):
                total_food += amount
                if amount > 500:
                    total_food_deduction += (amount - 500)
        
        total_salary = total_hours * self.hourly_rate
        net_salary = total_salary - total_food_deduction
        
        # Аванс (1-15 число)
        advance_hours = 0
        advance_deduction = 0
        for date_str, data in self.shifts.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month and
                1 <= date_obj.day <= 15 and
                data['type'] == 'work'):
                advance_hours += data['hours']
        
        for date_str, amount in self.food_expenses.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month and
                1 <= date_obj.day <= 15):
                if amount > 500:
                    advance_deduction += (amount - 500)
        
        advance = (advance_hours * self.hourly_rate) - advance_deduction
        
        # Остаток (16-конец месяца)
        remainder_hours = 0
        remainder_deduction = 0
        for date_str, data in self.shifts.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month and
                date_obj.day >= 16 and
                data['type'] == 'work'):
                remainder_hours += data['hours']
        
        for date_str, amount in self.food_expenses.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and 
                date_obj.month == self.current_date.month and
                date_obj.day >= 16):
                if amount > 500:
                    remainder_deduction += (amount - 500)
        
        remainder = (remainder_hours * self.hourly_rate) - remainder_deduction
        
        stats_text = (
            f'[b]📊 Статистика[/b]\n\n'
            f'Смен: [b]{total_shifts}[/b]  •  Часов: [b]{total_hours}[/b]\n'
            f'Зарплата: [b]{total_salary:,}[/b] ₽\n'
            f'Питание: [b]{total_food}[/b] ₽  •  Вычет: [color=ff4444][b]{total_food_deduction}[/b][/color] ₽\n'
            f'[color=22aa44][b]Итого: {net_salary:,} ₽[/b][/color]\n\n'
            f'[b]20-го числа:[/b] {advance:,} ₽\n'
            f'[b]5-го числа:[/b] {remainder:,} ₽'
        )
        
        self.stats_label.text = stats_text

    def show_settings(self, instance):
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        content.add_widget(Label(
            text='⚙ Настройки',
            size_hint_y=0.2,
            font_size='20sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        ))
        
        rate_layout = BoxLayout(size_hint_y=0.25, spacing=10)
        rate_layout.add_widget(Label(text='💰 Ставка (₽/час):', color=(0.1, 0.1, 0.1, 1)))
        rate_input = TextInput(
            text=str(self.hourly_rate),
            multiline=False,
            input_filter='int',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        rate_layout.add_widget(rate_input)
        content.add_widget(rate_layout)
        
        save_btn = Button(
            text='✓ Сохранить',
            size_hint_y=0.25,
            background_normal='',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        
        content.add_widget(save_btn)
        
        popup = Popup(
            title='Настройки',
            content=content,
            size_hint=(0.85, 0.45)
        )
        
        def save_settings(instance):
            self.hourly_rate = int(rate_input.text) if rate_input.text else 500
            self.save_data()
            self.update_stats()
            popup.dismiss()
        
        save_btn.bind(on_press=save_settings)
        popup.open()

    def show_food_menu(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        content.add_widget(Label(
            text='🍽 Статистика питания',
            size_hint_y=0.15,
            font_size='18sp',
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        ))
        
        # Подсчет по периодам
        total_food = 0
        total_deduction = 0
        
        for date_str, amount in self.food_expenses.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (date_obj.year == self.current_date.year and
                date_obj.month == self.current_date.month):
                total_food += amount
                if amount > 500:
                    total_deduction += (amount - 500)
        
        info_text = (
            f'Всего потрачено: {total_food} ₽\n'
            f'Лимит: 500 ₽ на день\n'
            f'Общий вычет из ЗП: {total_deduction} ₽'
        )
        
        info_label = Label(
            text=info_text,
            size_hint_y=0.4,
            color=(0.1, 0.1, 0.1, 1),
            font_size='15sp'
        )
        
        content.add_widget(info_label)
        
        close_btn = Button(
            text='Закрыть',
            size_hint_y=0.2,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Питание',
            content=content,
            size_hint=(0.8, 0.5)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def prev_month(self, instance):
        if self.current_date.month == 1:
            self.current_date = datetime(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month - 1, 1)
        self.update_calendar()

    def next_month(self, instance):
        if self.current_date.month == 12:
            self.current_date = datetime(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime(self.current_date.year, self.current_date.month + 1, 1)
        self.update_calendar()

    def save_data(self):
        data = {
            'shifts': self.shifts,
            'food_expenses': self.food_expenses,
            'hourly_rate': self.hourly_rate
        }
        with open('shift_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        if os.path.exists('shift_data.json'):
            try:
                with open('shift_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.shifts = data.get('shifts', {})
                    self.food_expenses = data.get('food_expenses', {})
                    self.hourly_rate = data.get('hourly_rate', 500)
            except:
                pass

if __name__ == '__main__':
    ShiftCalendarApp().run()
