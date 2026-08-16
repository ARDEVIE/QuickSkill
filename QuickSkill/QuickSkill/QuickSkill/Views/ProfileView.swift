import SwiftUI

struct ProfileView: View {
    // Глобальная переменная для статуса авторизации
    @AppStorage("isLoggedIn") var isLoggedIn = false
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(spacing: 24) {
                    
                    // Шапка с аватаром
                    VStack(spacing: 12) {
                        ZStack {
                            Circle()
                                .fill(LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.6), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing))
                                .frame(width: 90, height: 90)
                            
                            Text("ИС")
                                .font(.title)
                                .fontWeight(.heavy)
                                .foregroundColor(.white)
                        }
                        .shadow(color: Color.blue.opacity(0.3), radius: 10, x: 0, y: 5)
                        
                        VStack(spacing: 4) {
                            Text("Имя Студента")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("student@university.edu")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding(.top, 20)
                    
                    // Блок меню (Карточки)
                    VStack(spacing: 16) {
                        ProfileMenuRow(icon: "book.fill", title: "Мои курсы", iconColor: .blue)
                        ProfileMenuRow(icon: "heart.fill", title: "Избранное", iconColor: .red)
                        ProfileMenuRow(icon: "pencil.line", title: "Редактировать профиль", iconColor: .orange)
                        ProfileMenuRow(icon: "globe", title: "Язык приложения", iconColor: .green)
                    }
                    .padding(.horizontal)
                    
                    // Кнопка выхода
                    Button(action: {
                        // Меняем статус на "не авторизован", что вернет нас на экран входа
                        withAnimation {
                            isLoggedIn = false
                        }
                    }) {
                        HStack {
                            Image(systemName: "arrow.right.square")
                            Text("Выйти из аккаунта")
                                .fontWeight(.bold)
                        }
                        .foregroundColor(.red)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(16)
                    }
                    .padding(.horizontal)
                    .padding(.top, 10)
                    
                }
                .padding(.bottom, 30)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
        }
    }
}

// Вспомогательный компонент для строк меню
struct ProfileMenuRow: View {
    var icon: String
    var title: String
    var iconColor: Color
    
    var body: some View {
        HStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(iconColor.opacity(0.15))
                    .frame(width: 40, height: 40)
                
                Image(systemName: icon)
                    .foregroundColor(iconColor)
            }
            
            Text(title)
                .font(.headline)
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
                .font(.caption)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(16)
    }
}

#Preview {
    Group {
        ProfileView().preferredColorScheme(.light)
        ProfileView().preferredColorScheme(.dark)
    }
}
