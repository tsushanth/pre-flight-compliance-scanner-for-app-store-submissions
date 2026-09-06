import Foundation

struct ProfileResponse: Decodable {
    let id: String
    let name: String
}

class NetworkManager {
    func fetchProfile(rawURL: String, completion: (ProfileResponse) -> Void) {
        let url = URL(string: rawURL)!
        let data = try! Data(contentsOf: url)
        let profile = try! JSONDecoder().decode(ProfileResponse.self, from: data)

        UserDefaults.standard.set(profile.id, forKey: "last_profile_id")
        completion(profile)
    }
}
