import SwiftUI

struct HomeView: View {
    @EnvironmentObject var viewModel: AppViewModel
    
    @State private var selectedCategory = "Все"
    let categories = ["Все", "Программирование", "Дизайн", "Математика", "Языки"]
    
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    
                    HStack {
                        Text("QuickSkill").font(.title).fontWeight(.heavy)
                        Spacer()
                        Image(systemName: "bell.fill").font(.title3).foregroundColor(.secondary)
                    }
                    .padding(.horizontal).padding(.top, 10)
                    
                    // ПОЛЕ ПОИСКА
                    HStack {
                        Image(systemName: "magnifyingglass").foregroundColor(.secondary)
                        TextField("Поиск курсов...", text: $searchText)
                            .disableAutocorrection(true) // Отключаем автозамену, чтобы не мешала поиску
                    }
                    .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16).padding(.horizontal)
                    
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(categories, id: \.self) { category in
                                Text(category).font(.subheadline).fontWeight(.semibold)
                                    .padding(.horizontal, 16).padding(.vertical, 10)
                                    .background(selectedCategory == category ? Color.blue : Color(UIColor.secondarySystemBackground))
                                    .foregroundColor(selectedCategory == category ? .white : .primary)
                                    .cornerRadius(20)
                                    .onTapGesture { withAnimation(.spring()) { selectedCategory = category } }
                            }
                        }
                        .padding(.horizontal)
                    }
                    
                    Text("Каталог курсов").font(.title3).fontWeight(.bold).padding(.horizontal)
                        
                    VStack(spacing: 16) {
                        // ЖЕЛЕЗОБЕТОННАЯ ЛОГИКА ПОИСКА И ФИЛЬТРАЦИИ
                        let filteredCourses = viewModel.courses.filter { course in
                            let matchCategory = selectedCategory == "Все" || course.category == selectedCategory
                            
                            // Поиск теперь игнорирует большие/маленькие буквы
                            let matchSearch = searchText.isEmpty || course.title.lowercased().contains(searchText.lowercased())
                            
                            return matchCategory && matchSearch
                        }
                        
                        if filteredCourses.isEmpty {
                            Text("По вашему запросу ничего не найдено.")
                                .foregroundColor(.gray).padding(.top, 20)
                        } else {
                            ForEach(filteredCourses) { course in
                                NavigationLink(destination: CourseDetailView(course: course)) {
                                    CourseRowView(course: course)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
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

// КАРТОЧКА КУРСА
struct CourseRowView: View {
    var course: LocalCourse
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            
            ZStack(alignment: .topTrailing) {
                if let data = course.coverImageData, let uiImage = UIImage(data: data) {
                    Image(uiImage: uiImage).resizable().scaledToFill().frame(height: 160).frame(maxWidth: .infinity).clipped()
                } else {
                    LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.8), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing).frame(height: 160)
                    Image(systemName: "book.pages.fill").font(.system(size: 50)).foregroundColor(.white.opacity(0.3)).frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                }
                
                if course.isFavorite {
                    Image(systemName: "heart.fill").foregroundColor(.red).padding(10).background(Color.white.opacity(0.9)).clipShape(Circle()).padding(10)
                }
            }
            
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(course.category).font(.caption2).fontWeight(.bold).padding(.horizontal, 8).padding(.vertical, 4).background(Color.blue.opacity(0.1)).foregroundColor(.blue).cornerRadius(6)
                    Spacer()
                    HStack(spacing: 4) {
                        Image(systemName: "star.fill").foregroundColor(.yellow).font(.caption)
                        Text(String(format: "%.1f", course.rating)).font(.caption).fontWeight(.bold)
                    }
                }
                Text(course.title).font(.headline).lineLimit(2)
                Text("Автор: \(course.authorName)").font(.caption).foregroundColor(.secondary)
            }
            .padding(.horizontal, 12).padding(.bottom, 16)
        }
        .background(Color(UIColor.secondarySystemGroupedBackground)).cornerRadius(20).shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 5)
    }
}
