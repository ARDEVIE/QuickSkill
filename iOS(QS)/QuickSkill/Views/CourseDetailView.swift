import SwiftUI

struct CourseDetailView: View {
    // Позволяет закрывать этот экран и возвращаться назад
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                
                // Обложка курса (Градиент)
                ZStack(alignment: .topLeading) {
                    LinearGradient(gradient: Gradient(colors: [Color.blue.opacity(0.8), Color.blue]), startPoint: .topLeading, endPoint: .bottomTrailing)
                        .frame(height: 280)
                    
                    Image(systemName: "book.pages.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.white.opacity(0.3))
                        .frame(maxWidth: .infinity, alignment: .center)
                        .padding(.top, 80)
                    
                    // Кнопка "Назад"
                    Button(action: {
                        dismiss()
                    }) {
                        Image(systemName: "chevron.left")
                            .font(.title3)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .padding(12)
                            .background(Color.black.opacity(0.3))
                            .clipShape(Circle())
                    }
                    .padding(.leading, 16)
                    // Опускаем кнопку ниже челки iPhone
                    .padding(.top, 50)
                }
                
                // Контентная часть (наезжает на обложку)
                VStack(alignment: .leading, spacing: 24) {
                    
                    // Заголовок и рейтинг
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Программирование")
                                .font(.caption)
                                .fontWeight(.bold)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(Color.blue.opacity(0.1))
                                .foregroundColor(.blue)
                                .cornerRadius(8)
                            
                            Spacer()
                            
                            HStack(spacing: 4) {
                                Image(systemName: "star.fill")
                                    .foregroundColor(.yellow)
                                Text("4.9")
                                    .fontWeight(.bold)
                            }
                        }
                        
                        Text("Основы Swift UI")
                            .font(.title)
                            .fontWeight(.heavy)
                        
                        Text("Автор: Имя Студента")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    // Описание
                    VStack(alignment: .leading, spacing: 8) {
                        Text("О курсе")
                            .font(.title3)
                            .fontWeight(.bold)
                        
                        Text("Этот курс предназначен для тех, кто хочет быстро освоить разработку интерфейсов под iOS. Мы разберем основные компоненты, навигацию и работу с данными.")
                            .foregroundColor(.secondary)
                            .lineSpacing(4)
                    }
                    
                    // Материалы (PDF/Видео)
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Материалы")
                            .font(.title3)
                            .fontWeight(.bold)
                        
                        HStack(spacing: 16) {
                            Image(systemName: "doc.fill")
                                .foregroundColor(.red)
                                .font(.title2)
                            Text("Лекция_1_Основы.pdf")
                                .fontWeight(.semibold)
                            Spacer()
                            Image(systemName: "arrow.down.circle")
                                .foregroundColor(.blue)
                                .font(.title2)
                        }
                        .padding()
                        .background(Color(UIColor.secondarySystemBackground))
                        .cornerRadius(12)
                    }
                    
                    // Кнопка связи в Telegram (MVP функционал)
                    Button(action: {
                        // Эта ссылка откроет приложение Telegram на телефоне
                        if let url = URL(string: "tg://resolve?domain=telegram") {
                            UIApplication.shared.open(url)
                        }
                    }) {
                        HStack {
                            Image(systemName: "paperplane.fill")
                            Text("Связаться с автором")
                                .fontWeight(.bold)
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        // Цвет Telegram
                        .background(Color(red: 0.17, green: 0.65, blue: 0.86))
                        .cornerRadius(16)
                        .shadow(color: Color(red: 0.17, green: 0.65, blue: 0.86).opacity(0.4), radius: 10, x: 0, y: 5)
                    }
                    .padding(.top, 10)
                    
                }
                .padding(20)
                .background(Color(UIColor.systemBackground))
                // Скругляем только верхние углы
                .cornerRadius(24, corners: [.topLeft, .topRight])
                // Поднимаем блок вверх, чтобы он перекрывал картинку
                .offset(y: -30)
            }
        }
        .edgesIgnoringSafeArea(.top)
        .navigationBarHidden(true)
    }
}

// Вспомогательный код для скругления конкретных углов у контентного блока
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners
    
    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}

#Preview {
    Group {
        CourseDetailView().preferredColorScheme(.light)
        CourseDetailView().preferredColorScheme(.dark)
    }
}
