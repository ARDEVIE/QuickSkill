import { Component } from '@angular/core';

@Component({
  selector: 'app-courses',
  templateUrl: './courses.component.html',
  styleUrls: ['./courses.component.scss']
})
export class CoursesComponent {

  courses = [
    {
      id: 1,
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
      id: 2,
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
      id: 3,
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
      id: 4,
      title: 'Продвижение в социальных сетях',
      author: 'Алина Б.',
      category: 'Маркетинг',
      level: 'Средний',
      rating: '4.7',
      students: '73',
      lessons: '15 уроков',
      color: '#EAE7FF',
      icon: '↗'
    },

    {
      id: 5,
      title: 'Английский для IT',
      author: 'Елена Смирнова',
      category: 'Языки',
      level: 'Средний',
      rating: '4.9',
      students: '181',
      lessons: '20 уроков',
      color: '#E8F0FF',
      icon: 'A'
    },

    {
      id: 6,
      title: 'Основы Figma',
      author: 'Диана А.',
      category: 'Дизайн',
      level: 'Начальный',
      rating: '4.8',
      students: '105',
      lessons: '14 уроков',
      color: '#FFF4D9',
      icon: 'F'
    },

    {
      id: 7,
      title: 'Основы Python',
      author: 'Илья Петров',
      category: 'Программирование',
      level: 'Средний',
      rating: '4.7',
      students: '89',
      lessons: '16 уроков',
      color: '#E7F5FF',
      icon: '{ }'
    },

    {
      id: 8,
      title: 'Личный бренд',
      author: 'Алина Б.',
      category: 'Бизнес',
      level: 'Начальный',
      rating: '4.6',
      students: '62',
      lessons: '10 уроков',
      color: '#F2E9FF',
      icon: '★'
    }
  ];

}