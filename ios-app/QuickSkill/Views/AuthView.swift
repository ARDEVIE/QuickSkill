import SwiftUI

struct AuthView: View {
    // Эта переменная автоматически сохраняется в память самого iPhone!
    @AppStorage("isLoggedIn") var isLoggedIn = false
    
    @State private var isLoginMode = true
    @State private var email = ""
    @State private var password = ""
    @State private var name = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Spacer()
                
                Image(systemName: "graduationcap.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.blue)
                    .padding(.bottom, 20)
                
                Text(isLoginMode ? "С возвращением!" : "Создать аккаунт")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                VStack(spacing: 16) {
                    if !isLoginMode {
                        TextField("Имя и Фамилия", text: $name)
                            .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                    }
                    
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress).autocapitalization(.none)
                        .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                    
                    SecureField("Пароль", text: $password)
                        .padding().background(Color(UIColor.secondarySystemBackground)).cornerRadius(16)
                }
                .padding(.horizontal)
                
                Button(action: {
                    if !email.isEmpty && !password.isEmpty {
                        withAnimation {
                            // Меняем статус -> приложение пускает нас внутрь и сохраняет это навсегда
                            isLoggedIn = true
                        }
                    }
                }) {
                    Text(isLoginMode ? "Войти" : "Зарегистрироваться")
                        .font(.headline).foregroundColor(.white).frame(maxWidth: .infinity)
                        .padding().background(email.isEmpty || password.isEmpty ? Color.gray : Color.blue).cornerRadius(16)
                }
                .disabled(email.isEmpty || password.isEmpty)
                .padding(.horizontal).padding(.top, 10)
                
                Spacer()
                
                Button(action: { withAnimation { isLoginMode.toggle() } }) {
                    Text(isLoginMode ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти")
                        .font(.subheadline).foregroundColor(.blue)
                }
                .padding(.bottom, 20)
            }
        }
    }
}
