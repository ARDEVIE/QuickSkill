import SwiftUI

struct CatalogView: View {
    @EnvironmentObject var viewModel: AppViewModel
    
    // Переменная, которая хранит то, что ты вводишь в строку поиска
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 16) {
                
                Text("Каталог")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .padding(.horizontal)
                    .padding(.top, 10)
                
                // СТРОКА ПОИСКА
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gray)
                    TextField("Название курса...", text: $searchText)
                        .disableAutocorrection(true) // Отключаем автозамену слов
                        .textInputAutocapitalization(.never)
                }
                .padding(12)
                .background(Color(UIColor.secondarySystemBackground))
                .cornerRadius(12)
                .padding(.horizontal)
                
                // ЛОГИКА ОТОБРАЖЕНИЯ ЭКРАНА
                if searchText.isEmpty {
                    
                    // 1. ЕСЛИ СТРОКА ПУСТАЯ -> ПОКАЗЫВАЕМ ЗАГЛУШКУ
                    Spacer()
                    VStack(spacing: 12) {
                        Image(systemName: "books.vertical.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.gray.opacity(0.4))
                        Text("Введите название темы")
                            .font(.headline)
                        Text("Здесь появятся результаты поиска")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity)
                    Spacer()
                    
                } else {
                    
                    // 2. ЕСЛИ ЧТО-ТО ВВЕЛИ -> ФИЛЬТРУЕМ БАЗУ ДАННЫХ
                    let filteredCourses = viewModel.courses.filter { course in
                        course.title.lowercased().contains(searchText.lowercased())
                    }
                    
                    if filteredCourses.isEmpty {
                        
                        // 3. ЕСЛИ ТАКОГО КУРСА НЕТ
                        Spacer()
                        Text("Курс не найден")
                            .foregroundColor(.gray)
                            .frame(maxWidth: .infinity)
                        Spacer()
                        
                    } else {
                        
                        // 4. ЕСЛИ КУРС НАЙДЕН -> ВЫВОДИМ СПИСОК
                        ScrollView(showsIndicators: false) {
                            VStack(spacing: 16) {
                                ForEach(filteredCourses) { course in
                                    NavigationLink(destination: CourseDetailView(course: course)) {
                                        CourseRowView(course: course)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                            .padding(.horizontal)
                            .padding(.top, 10)
                        }
                    }
                }
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
        }
    }
}

#Preview {
    CatalogView().environmentObject(AppViewModel())
}
