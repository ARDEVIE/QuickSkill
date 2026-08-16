import SwiftUI

struct AddCourseView: View {
    @State private var courseTitle = ""
    @State private var courseDescription = ""
    @State private var selectedCategory = "Программирование"
    let categories = ["Программирование", "Дизайн", "Математика", "Языки"]
    
    // Переменная для имитации прикрепленного файла
    @State private var attachedFileName: String? = nil
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 24) {
                    
                    // Шапка с логотипом
                    HStack {
                        Spacer()
                        Image("logo")
                            .resizable()
                            .scaledToFit()
                            .frame(height: 35)
                        Spacer()
                    }
                    .padding(.top, 10)
                    
                    Text("Создать новый курс")
                        .font(.title2)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                    
                    // 1. Название курса
                    VStack(alignment: .leading, spacing: 8) {
                        Text("НАЗВАНИЕ КУРСА")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                        
                        TextField("Например: Высшая математика", text: $courseTitle)
                            .padding()
                            .background(Color(UIColor.secondarySystemBackground))
                            .cornerRadius(16)
                    }
                    .padding(.horizontal)
                    
                    // 2. Выбор категории
                    VStack(alignment: .leading, spacing: 8) {
                        Text("КАТЕГОРИЯ")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                            .padding(.horizontal)
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                ForEach(categories, id: \.self) { category in
                                    Text(category)
                                        .font(.subheadline)
                                        .fontWeight(.semibold)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
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
                    }
                    
                    // 3. Описание
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ОПИСАНИЕ")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                        
                        TextEditor(text: $courseDescription)
                            .frame(height: 100)
                            .padding(8)
                            .background(Color(UIColor.secondarySystemBackground))
                            .cornerRadius(16)
                    }
                    .padding(.horizontal)
                    
                    // 4. Загрузка фото (Обложка)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("ОБЛОЖКА КУРСА")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                        
                        Button(action: {
                            print("Открытие галереи...")
                        }) {
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .strokeBorder(style: StrokeStyle(lineWidth: 2, dash: [10]))
                                    .foregroundColor(Color.blue.opacity(0.5))
                                    .frame(height: 120)
                                    .background(Color.blue.opacity(0.05).cornerRadius(16))
                                
                                VStack(spacing: 8) {
                                    Image(systemName: "photo.on.rectangle.angled")
                                        .font(.title)
                                    Text("Загрузить изображение")
                                        .font(.subheadline)
                                }
                                .foregroundColor(.blue)
                            }
                        }
                    }
                    .padding(.horizontal)
                    
                    // 5. Загрузка материалов (PDF / Видео)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("МАТЕРИАЛЫ КУРСА")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.secondary)
                        
                        Button(action: {
                            // Имитация выбора файла для UI
                            withAnimation(.spring()) {
                                if attachedFileName == nil {
                                    attachedFileName = "Лекция_1.pdf"
                                } else {
                                    attachedFileName = nil
                                }
                            }
                        }) {
                            HStack(spacing: 16) {
                                // Иконка документа
                                ZStack {
                                    Circle()
                                        .fill(attachedFileName == nil ? Color.blue.opacity(0.15) : Color.green.opacity(0.15))
                                        .frame(width: 44, height: 44)
                                    Image(systemName: attachedFileName == nil ? "doc.badge.plus" : "doc.fill")
                                        .foregroundColor(attachedFileName == nil ? .blue : .green)
                                        .font(.title3)
                                }
                                
                                // Текст
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(attachedFileName == nil ? "Прикрепить файл" : attachedFileName!)
                                        .font(.headline)
                                        .foregroundColor(.primary)
                                    Text(attachedFileName == nil ? "Поддерживаются .pdf, .mp4" : "Файл успешно добавлен")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                // Плюсик или галочка
                                Image(systemName: attachedFileName == nil ? "plus.circle.fill" : "checkmark.circle.fill")
                                    .foregroundColor(attachedFileName == nil ? .blue : .green)
                                    .font(.title2)
                            }
                            .padding()
                            .background(Color(UIColor.secondarySystemBackground))
                            .cornerRadius(16)
                            // Если файл добавлен, делаем зеленую рамку для красоты
                            .overlay(
                                RoundedRectangle(cornerRadius: 16)
                                    .stroke(attachedFileName != nil ? Color.green.opacity(0.5) : Color.clear, lineWidth: 1)
                            )
                        }
                    }
                    .padding(.horizontal)
                    
                    // Кнопка публикации
                    Button(action: {
                        print("Публикация...")
                    }) {
                        Text("Опубликовать курс")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(16)
                            .shadow(color: Color.blue.opacity(0.3), radius: 10, x: 0, y: 5)
                    }
                    .padding(.horizontal)
                    .padding(.top, 10)
                    
                }
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
        }
    }
}

#Preview {
    Group {
        AddCourseView().preferredColorScheme(.light)
        AddCourseView().preferredColorScheme(.dark)
    }
}
