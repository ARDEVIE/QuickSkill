import SwiftUI

struct AuthView: View {
    // Переменная, которая переключает состояния: Вход или Регистрация
    @State private var isLogin = true
    
    @State private var email = ""
    @State private var password = ""
    @State private var name = "" // Используется только для регистрации
    
    // Глобальная переменная для статуса авторизации
    @AppStorage("isLoggedIn") var isLoggedIn = false
    
    var body: some View {
        VStack(spacing: 24) {
            Spacer()
            
            // Наш новый логотип
            Image("logo")
                .resizable()
                .scaledToFit()
                .frame(height: 50)
                .padding(.bottom, 20)
            
            // Динамический заголовок
            Text(isLogin ? "Вход" : "Регистрация")
                .font(.title2)
                .fontWeight(.bold)
            
            // Блок с полями ввода
            VStack(spacing: 16) {
                // Поле имени показываем только при регистрации
                if !isLogin {
                    CustomTextField(placeholder: "Ваше имя", text: $name, icon: "person")
                        // Анимация появления поля
                        .transition(.opacity.combined(with: .move(edge: .top)))
                }
                
                CustomTextField(placeholder: "Email", text: $email, icon: "envelope")
                
                CustomSecureField(placeholder: "Пароль", text: $password, icon: "lock")
            }
            .padding(.horizontal)
            
            // Главная кнопка действия
            Button(action: {
                // Имитируем успешный вход/регистрацию
                withAnimation {
                    isLoggedIn = true
                }
            }) {
                Text(isLogin ? "Войти" : "Зарегистрироваться")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(16)
                    // Цветная тень в цвет кнопки
                    .shadow(color: Color.blue.opacity(0.3), radius: 10, x: 0, y: 5)
            }
            .padding(.horizontal)
            .padding(.top, 10)
            
            // Кнопка переключения между Входом и Регистрацией
            Button(action: {
                withAnimation(.spring()) {
                    isLogin.toggle()
                }
            }) {
                Text(isLogin ? "Нет аккаунта? Зарегистрироваться" : "Есть аккаунт? Войти")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding(.top, 10)
            
            Spacer()
        }
        .background(Color(UIColor.systemBackground))
    }
}

// Вспомогательный компонент: Красивое текстовое поле с иконкой
struct CustomTextField: View {
    var placeholder: String
    @Binding var text: String
    var icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.secondary)
                .frame(width: 24)
            TextField(placeholder, text: $text)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(16)
    }
}

// Вспомогательный компонент: Поле для скрытого пароля
struct CustomSecureField: View {
    var placeholder: String
    @Binding var text: String
    var icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.secondary)
                .frame(width: 24)
            SecureField(placeholder, text: $text)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(16)
    }
}

#Preview {
    Group {
        AuthView()
            .preferredColorScheme(.light)
        AuthView()
            .preferredColorScheme(.dark)
    }
}
