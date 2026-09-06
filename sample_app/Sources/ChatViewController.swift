import UIKit

/// Simple in-app chat screen backed by a socket connection.
class ChatViewController: UIViewController {
    private var messages: [String] = []

    func sendMessage(_ text: String) {
        messages.append(text)
        broadcast(text)
    }

    private func broadcast(_ text: String) {
        // Send `text` to all other participants in the room.
        print("broadcasting: \(text)")
    }
}
