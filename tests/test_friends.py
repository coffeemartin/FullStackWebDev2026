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
