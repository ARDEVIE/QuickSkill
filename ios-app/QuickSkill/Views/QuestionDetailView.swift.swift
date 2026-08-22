import SwiftUI

struct QuestionDetailView: View {
    var question: LocalQuestion
    @EnvironmentObject var viewModel: AppViewModel
    @Environment(\.dismiss) var dismiss
    
    @State private var newCommentText = ""
    
    // Находим вопрос в базе данных, чтобы экран обновлялся сразу после отправки комментария
    var currentQuestion: LocalQuestion? {
        viewModel.questions.first(where: { $0.id == question.id })
    }
    
    var body: some View {
        VStack(spacing: 0) {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if let q = currentQuestion {
                        Text(q.title)
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        Text("Автор: \(q.author)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Divider()
                        
                        Text("Комментарии (\(q.answersCount))")
                            .font(.headline)
                        
                        // ВЫВОД КОММЕНТАРИЕВ
                        if q.comments.isEmpty {
                            Text("Пока нет ответов. Будьте первым!")
                                .foregroundColor(.gray)
                                .italic()
                                .padding(.top, 10)
                        } else {
                            ForEach(q.comments) { comment in
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(comment.author)
                                        .font(.caption)
                                        .fontWeight(.bold)
                                        .foregroundColor(.blue)
                                    Text(comment.text)
                                        .font(.subheadline)
                                }
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color(UIColor.secondarySystemBackground))
                                .cornerRadius(12)
                            }
                        }
                    }
                }
                .padding()
            }
            
            // ПОЛЕ ВВОДА НОВОГО КОММЕНТАРИЯ
            VStack {
                Divider()
                HStack {
                    TextField("Написать ответ...", text: $newCommentText)
                        .padding(10)
                        .background(Color(UIColor.secondarySystemBackground))
                        .cornerRadius(20)
                    
                    Button(action: {
                        if !newCommentText.isEmpty, let qId = currentQuestion?.id {
                            viewModel.addComment(to: qId, text: newCommentText)
                            newCommentText = "" // Очищаем поле после отправки
                        }
                    }) {
                        Image(systemName: "paperplane.fill")
                            .foregroundColor(.white)
                            .padding(10)
                            .background(newCommentText.isEmpty ? Color.gray : Color.blue)
                            .clipShape(Circle())
                    }
                    .disabled(newCommentText.isEmpty)
                }
                .padding()
            }
            .background(Color(UIColor.systemBackground))
        }
        .navigationTitle("Обсуждение")
        .navigationBarTitleDisplayMode(.inline)
        // КНОПКА УДАЛЕНИЯ ВОПРОСА В ВЕРХНЕМ МЕНЮ
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(role: .destructive, action: {
                    if let qId = currentQuestion?.id {
                        viewModel.deleteQuestion(id: qId)
                        dismiss()
                    }
                }) {
                    Image(systemName: "trash")
                        .foregroundColor(.red)
                }
            }
        }
    }
}
