import Foundation

struct Email: Identifiable, Decodable {
    var id: String
    var From: String
    var Subject: String
    var body: String
}

