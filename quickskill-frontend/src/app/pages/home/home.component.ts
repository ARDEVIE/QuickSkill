import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent {

  categories = [
    { name: 'Программирование', icon: '</>', courses: 42 },
    { name: 'Дизайн', icon: '✦', courses: 27 },
    { name: 'Маркетинг', icon: '↗', courses: 18 },
    { name: 'Языки', icon: 'Aa', courses: 31 },
    { name: 'Бизнес', icon: '◈', courses: 15 },
    { name: 'Другое', icon: '+', courses: 24 }
  ];

  courses = [
    {
      title: 'Основы веб-разработки',
      author: 'Алексей Иванов',
      category: 'Программирование',
      level: 'Начальный',
      rating: '4.9',
      students: '128',
      lessons: '12 уроков',
      color: '#DCEAFF',
      icon: '</>'
    },
    {
      title: 'UI/UX дизайн с нуля',
      author: 'Мария Ким',
      category: 'Дизайн',
      level: 'Начальный',
      rating: '4.8',
      students: '96',
      lessons: '18 уроков',
      color: '#FFF0E4',
      icon: '✦'
    },
    {
      title: 'Python для начинающих',
      author: 'Данияр С.',
      category: 'Программирование',
      level: 'Начальный',
      rating: '4.9',
      students: '214',
      lessons: '24 урока',
      color: '#E5F7F1',
      icon: 'Py'
    },
    {
      title: 'Продвижение в социальных сетях',
      author: 'Алина Б.',
      category: 'Маркетинг',
      level: 'Средний',
      rating: '4.7',
      students: '73',
      lessons: '15 уроков',
      color: '#EAE7FF',
      icon: '↗'
    }
  ];
}