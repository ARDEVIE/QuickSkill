import Foundation
import Combine
import SwiftUI

struct LocalCourse: Identifiable {
    let id = UUID()
    var title: String
    var description: String
    var category: String
    var authorName: String
    var telegramLink: String
    var rating: Double = 0.0
    var isFavorite: Bool = false
    var attachedFileName: String? = nil
    var coverImageData: Data? = nil
}

struct LocalComment: Identifiable { let id = UUID(); var text: String; var author: String }
struct LocalQuestion: Identifiable { let id = UUID(); var title: String; var author: String; var answersCount: Int; var comments: [LocalComment] = [] }

class AppViewModel: ObservableObject {
    @Published var courses: [LocalCourse] = []
    @Published var questions: [LocalQuestion] = []
    
    init() { loadInitialData() }
    
    private func loadInitialData() {
        let sample1 = LocalCourse(title: "Основы Swift UI", description: "Создание красивых приложений.", category: "Программирование", authorName: "Имя Студента", telegramLink: "https://t.me/durov", rating: 4.9, isFavorite: true)
        courses = [sample1]
    }
    
    func addCourse(title: String, description: String, category: String, telegramLink: String, fileName: String?, coverImageData: Data?) {
        let newCourse = LocalCourse(title: title, description: description, category: category, authorName: "Имя Студента", telegramLink: telegramLink, attachedFileName: fileName, coverImageData: coverImageData)
        courses.insert(newCourse, at: 0)
    }
    
    func addQuestion(title: String, author: String) { questions.insert(LocalQuestion(title: title, author: author, answersCount: 0), at: 0) }
    func deleteCourse(id: UUID) { courses.removeAll { $0.id == id } }
    func deleteQuestion(id: UUID) { questions.removeAll { $0.id == id } }
    func addComment(to questionId: UUID, text: String) {
        if let index = questions.firstIndex(where: { $0.id == questionId }) {
            questions[index].comments.append(LocalComment(text: text, author: "Имя Студента"))
            questions[index].answersCount = questions[index].comments.count
        }
    }
    func toggleFavorite(id: UUID) {
        if let index = courses.firstIndex(where: { $0.id == id }) { courses[index].isFavorite.toggle() }
    }
    
    // НОВАЯ ФУНКЦИЯ ОЦЕНКИ
    func rateCourse(id: UUID, newRating: Double) {
        if let index = courses.firstIndex(where: { $0.id == id }) {
            courses[index].rating = newRating
        }
    }
}
