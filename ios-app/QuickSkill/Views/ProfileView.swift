import SwiftUI

struct ProfileView: View {
    @AppStorage("isLoggedIn") var isLoggedIn = false
    @AppStorage("isDarkMode") var isDarkMode = false
    
    // ПАМЯТЬ ДЛЯ ИМЕНИ ПОЛЬЗОВАТЕЛЯ
    @AppStorage("userName") var userName = "Имя Студента"
    
    @State private var showEditNameAlert = false
    @State private var tempName = ""
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(spacing: 24) {
                    
                    // Шапка
                    VStack(spacing: 12) {
                        ZStack {
                            Circle().fill(LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing)).frame(width: 90, height: 90)
                            Text(String(userName.prefix(1)).uppercased()).font(.title).fontWeight(.heavy).foregroundColor(.white)
                        }
                        VStack(spacing: 4) {
                            Text(userName).font(.title2).fontWeight(.bold)
                            Text("student@university.edu").font(.subheadline).foregroundColor(.secondary)
                        }
                    }
                    .padding(.top, 20)
                    
                    // Блок меню
                    VStack(spacing: 16) {
                        
                        NavigationLink(destination: MyCoursesView()) {
                            MenuButton(icon: "book.fill", title: "Мои курсы", iconColor: .blue)
                        }
                        
                        NavigationLink(destination: FavoritesView()) {
                            MenuButton(icon: "heart.fill", title: "Избранное", iconColor: .red)
                        }
                        
                        Button(action: {
                            tempName = userName
                            showEditNameAlert = true
                        }) {
                            MenuButton(icon: "pencil.line", title: "Изменить имя", iconColor: .orange)
                        }
                        
                        HStack(spacing: 16) {
                            ZStack {
                                Circle().fill(Color.purple.opacity(0.15)).frame(width: 40, height: 40)
                                Image(systemName: isDarkMode ? "moon.fill" : "sun.max.fill").foregroundColor(.purple)
                            }
                            Toggle("Темная тема", isOn: $isDarkMode).font(.headline).foregroundColor(.primary)
                        }
                        .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                    }
                    .padding(.horizontal)
                    
                    // Выход
                    Button(action: {
                        withAnimation { isLoggedIn = false }
                    }) {
                        HStack {
                            Image(systemName: "arrow.right.square")
                            Text("Выйти из аккаунта").fontWeight(.bold)
                        }
                        .foregroundColor(.red).frame(maxWidth: .infinity).padding().background(Color.red.opacity(0.1)).cornerRadius(16)
                    }
                    .padding(.horizontal).padding(.top, 10)
                    
                }
                .padding(.bottom, 30)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
            
            .alert("Изменить имя", isPresented: $showEditNameAlert) {
                TextField("Введите ваше имя", text: $tempName)
                Button("Отмена", role: .cancel) { }
                Button("Сохранить") {
                    if !tempName.isEmpty {
                        userName = tempName
                    }
                }
            } message: {
                Text("Это имя будут видеть другие пользователи в ваших курсах.")
            }
        }
    }
}

// Визуал кнопок меню
struct MenuButton: View {
    var icon: String; var title: String; var iconColor: Color
    var body: some View {
        HStack(spacing: 16) {
            ZStack { Circle().fill(iconColor.opacity(0.15)).frame(width: 40, height: 40); Image(systemName: icon).foregroundColor(iconColor) }
            Text(title).font(.headline).foregroundColor(.primary)
            Spacer()
            Image(systemName: "chevron.right").foregroundColor(.secondary).font(.caption)
        }
        .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
    }
}

// ЭКРАН "МОИ КУРСЫ"
struct MyCoursesView: View {
    @EnvironmentObject var viewModel: AppViewModel
    @AppStorage("userName") var userName = "Имя Студента"
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                let myCourses = viewModel.courses.filter { $0.authorName == userName || $0.authorName == "Имя Студента" }
                
                if myCourses.isEmpty {
                    Text("Вы еще не создали ни одного курса.").foregroundColor(.gray).padding(.top, 50)
                } else {
                    ForEach(myCourses) { course in
                        NavigationLink(destination: CourseDetailView(course: course)) {
                            CourseRowView(course: course)
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                }
            }
            .padding()
        }
        .navigationTitle("Мои курсы").navigationBarTitleDisplayMode(.inline).background(Color(UIColor.systemBackground))
    }
}

#Preview {
    ProfileView().environmentObject(AppViewModel())
}
