import SwiftUI

struct HomeView: View {
    @State private var searchText = ""
    
    // Горизонтальные категории
    let categories = ["Все", "Программирование", "Дизайн", "Математика", "Языки"]
    @State private var selectedCategory = "Все"
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    
                    // Шапка с логотипом и приветствием
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Привет, Студент! 👋")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            Text("Что будем изучать?")
                                .font(.title2)
                                .fontWeight(.bold)
                        }
                        Spacer()
                        
                        // ТВОЙ ЛОГОТИП
                        Image("logo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 35)
                    }
                    .padding(.horizontal)
                    .padding(.top, 10)
                    
                    // Стильная строка поиска
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.secondary)
                        TextField("Поиск курсов...", text: $searchText)
                    }
                    .padding()
                    .background(Color(UIColor.secondarySystemBackground))
                    .cornerRadius(16)
                    .padding(.horizontal)
                    
                    // Горизонтальный список категорий (Pills)
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(categories, id: \.self) { category in
                                Text(category)
                                    .font(.subheadline)
                                    .fontWeight(.semibold)
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 10)
                                    // Синий цвет берем как основной акцент под твой логотип
                                    .background(selectedCategory == category ? Color.blue : Color(UIColor.secondarySystemBackground))
                                    .foregroundColor(selectedCategory == category ? .white : .primary)
                                    .cornerRadius(20)
                                    .onTapGesture {
                                        withAnimation(.spring()) {
                                            selectedCategory = category
                                        }
                                    }
                            }
                        }
                        .padding(.horizontal)
                    }
                    
                    Text("Популярные курсы")
                        .font(.title3)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                        .padding(.top, 10)
                    
                    // Список курсов с новыми карточками
                    VStack(spacing: 16) {
                        ForEach(0..<5, id: \.self) { _ in
                            
                            // Обернули карточку в кнопку перехода
                            NavigationLink(destination: CourseDetailView()) {
                                CourseRowView()
                            }
                            .buttonStyle(PlainButtonStyle()) // Убираем стандартное синее выделение кнопки
                            
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
        }
    }
}

// Обновленная, сочная карточка курса
struct CourseRowView: View {
    var body: some View {
        HStack(spacing: 16) {
            
            // Иконка курса с градиентом
            ZStack {
                LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing)
                
                Image(systemName: "book.pages.fill")
                    .font(.title)
                    .foregroundColor(.white)
            }
            .frame(width: 80, height: 80)
            .cornerRadius(16)
            
            // Информация о курсе
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text("IT / Программирование")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                    Spacer()
                    Image(systemName: "star.fill")
                        .font(.caption)
                        .foregroundColor(.yellow)
                    Text("4.9")
                        .font(.caption)
                        .fontWeight(.bold)
                }
                
                Text("Основы Swift UI")
                    .font(.headline)
                    .lineLimit(1)
                
                Text("Узнай, как создавать красивые приложения с нуля.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }
        }
        .padding(12)
        .background(Color(UIColor.secondarySystemGroupedBackground))
        .cornerRadius(20)
        // Добавляем современную мягкую тень
        .shadow(color: Color.black.opacity(0.06), radius: 10, x: 0, y: 4)
    }
}

#Preview {
    Group {
        HomeView()
            .preferredColorScheme(.light)
        HomeView()
            .preferredColorScheme(.dark)
    }
}
