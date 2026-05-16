from tests.conftest import login, make_user


def test_friend_search_returns_partial_name_matches(client):
    make_user("faiz", name="Faiz")
    make_user("franco", name="Franco")
    make_user("rushil", name="Rushil")
    login(client, "faiz")

    response = client.get("/friends/search?q=f")
    data = response.get_json()

    assert response.status_code == 200
    assert any(user["username"] == "franco" for user in data["results"])
    assert all(user["username"] != "rushil" for user in data["results"])


def test_friend_profile_requires_accepted_friendship(client):
    make_user("faiz", name="Faiz")
    franco = make_user("franco", name="Franco")
    login(client, "faiz")

    response = client.get(f"/profile/{franco.id}", follow_redirects=True)

    assert response.status_code == 200
    assert b"You can view this profile after the friend request is accepted." in response.data
