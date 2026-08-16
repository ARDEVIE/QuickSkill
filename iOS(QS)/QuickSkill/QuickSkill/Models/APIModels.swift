import Foundation

// Модель для ответа при успешном логине (Django SimpleJWT)
struct AuthResponse: Codable {
    let access: String
    let refresh: String
}

// Модель Пользователя (/api/users/me/)
struct User: Codable, Identifiable {
    let id: Int
    let username: String
    let email: String
    let firstName: String?
    let lastName: String?
    
    // В Swift принято использовать camelCase, а в Django (Python) snake_case.
    // CodingKeys "переводит" поля для парсера
    enum CodingKeys: String, CodingKey {
        case id, username, email
        case firstName = "first_name"
        case lastName = "last_name"
    }
}

// Модель Категории (/api/categories/)
struct Category: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let slug: String?
}

// Модель Курса (/api/courses/)
struct Course: Codable, Identifiable {
    let id: Int
    let title: String
    let description: String
    let authorId: Int
    let categoryId: Int
    // Урл до картинки обложки (если она есть на бэкенде)
    let coverImage: String?
    let isPublished: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, title, description
        case authorId = "author" // Или "author_id" в зависимости от твоего DRF сериализатора
        case categoryId = "category"
        case coverImage = "cover_image"
        case isPublished = "is_published"
    }
}

// Модель Материала (/api/materials/)
struct CourseMaterial: Codable, Identifiable {
    let id: Int
    let courseId: Int
    let title: String
    let fileUrl: String
    let materialType: String // например "pdf" или "video"
    
    enum CodingKeys: String, CodingKey {
        case id, title
        case courseId = "course"
        case fileUrl = "file"
        case materialType = "material_type"
    }
}
