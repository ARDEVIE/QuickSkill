import SwiftUI

struct ForumView: View {
    @EnvironmentObject var viewModel: AppViewModel
    
    @State private var searchText = ""
    @State private var showAddQuestion = false
    @State private var newQuestionTitle = ""
    
    // Берем имя пользователя из памяти телефона для публикации
    @AppStorage("userName") var userName = "Имя Студента"
    
    var body: some View {
        NavigationView {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 20) {
                    
                    // ШАПКА ФОРУМА (ТЕПЕРЬ АДАПТИВНАЯ К ТЕМНОЙ ТЕМЕ)
                    VStack(alignment: .leading, spacing: 8) {
                        Text("FORUM")
                            .font(.caption)
                            .fontWeight(.bold)
                            .foregroundColor(.blue)
                        
                        Text("Обсуждения и вопросы")
                            .font(.title2)
                            .fontWeight(.bold)
                            .foregroundColor(.primary) // Автоматически черный днем, белый ночью
                        
                        Text("Задавай вопросы и делись опытом.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(20)
                    // Используем opacity: на черном фоне это даст красивый темно-синий оттенок
                    .background(Color.blue.opacity(0.15))
                    .cornerRadius(20)
                    .padding(.horizontal)
                    .padding(.top, 10)
                    
                    // СТРОКА ПОИСКА И КНОПКА СОЗДАНИЯ ВОПРОСА
                    HStack(spacing: 12) {
                        HStack {
                            Image(systemName: "magnifyingglass").foregroundColor(.gray)
                            TextField("Поиск вопросов...", text: $searchText)
                                .disableAutocorrection(true)
                        }
                        .padding(12)
                        .background(Color(UIColor.secondarySystemBackground))
                        .cornerRadius(12)
                        
                        // Кнопка добавления
                        Button(action: { showAddQuestion = true }) {
                            Image(systemName: "plus.bubble.fill")
                                .font(.title3)
                                .foregroundColor(.white)
                                .padding(12)
                                .background(Color.blue)
                                .cornerRadius(12)
                        }
                    }
                    .padding(.horizontal)
                    
                    Text("Последние вопросы")
                        .font(.title3)
                        .fontWeight(.bold)
                        .padding(.horizontal)
                    
                    // СПИСОК ВОПРОСОВ С ФИЛЬТРАЦИЕЙ ПОИСКА
                    let filteredQuestions = viewModel.questions.filter {
                        searchText.isEmpty || $0.title.lowercased().contains(searchText.lowercased())
                    }
                    
                    if filteredQuestions.isEmpty {
                        VStack(spacing: 12) {
                            Image(systemName: "tray.fill").font(.largeTitle).foregroundColor(.gray.opacity(0.5))
                            Text("Вопросов пока нет.")
                                .foregroundColor(.gray)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.top, 40)
                    } else {
                        VStack(spacing: 12) {
                            ForEach(filteredQuestions) { question in
                                NavigationLink(destination: QuestionDetailView(question: question)) {
                                    QuestionRowView(question: question)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding(.horizontal)
                    }
                }
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .background(Color(UIColor.systemBackground))
            
            // ВСПЛЫВАЮЩЕЕ ОКНО ДЛЯ СОЗДАНИЯ ВОПРОСА
            .alert("Новый вопрос", isPresented: $showAddQuestion) {
                TextField("Напишите ваш вопрос...", text: $newQuestionTitle)
                Button("Отмена", role: .cancel) { }
                Button("Опубликовать") {
                    if !newQuestionTitle.isEmpty {
                        viewModel.addQuestion(title: newQuestionTitle, author: userName)
                        newQuestionTitle = ""
                    }
                }
            }
        }
    }
}

// КАРТОЧКА ОТДЕЛЬНОГО ВОПРОСА В ЛЕНТЕ
struct QuestionRowView: View {
    var question: LocalQuestion
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(question.title)
                .font(.headline)
                .lineLimit(2)
            
            HStack {
                Text("Автор: \(question.author)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                HStack(spacing: 4) {
                    Image(systemName: "bubble.right.fill").foregroundColor(.blue)
                    Text("\(question.answersCount)")
                        .font(.caption)
                        .fontWeight(.bold)
                }
            }
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(16)
    }
}

#Preview {
    Group {
        ForumView().preferredColorScheme(.light).environmentObject(AppViewModel())
        ForumView().preferredColorScheme(.dark).environmentObject(AppViewModel())
    }
}
