import os
import requests
from instaloader import Instaloader, Profile
from instagrapi import Client


def download_profile_picture(profile, destination_folder):
    """Download the profile picture of the source account."""
    print(f"Downloading profile picture of {profile.username}...")
    pfp_url = profile.profile_pic_url
    response = requests.get(pfp_url)
    if response.status_code == 200:
        file_path = os.path.join(destination_folder, "profile_pic.jpg")
        with open(file_path, "wb") as file:
            file.write(response.content)
        print("Profile picture downloaded!")
        return file_path
    else:
        print("Failed to download profile picture.")
        return None


def download_posts(profile, destination_folder, loader):
    """Download all posts of the source account."""
    print(f"Downloading posts of {profile.username}...")
    posts_folder = os.path.join(destination_folder, "posts")
    if not os.path.exists(posts_folder):
        os.makedirs(posts_folder)

    posts = profile.get_posts()
    for i, post in enumerate(posts, start=1):
        loader.download_post(post, target=posts_folder)
        print(f"Downloaded post {i}")


def upload_to_target_account(client, destination_folder, target_username, bio):
    """Upload profile picture and posts to the target account."""
    print(f"Uploading profile picture and posts to {target_username}...")
    
    # Upload profile picture
    profile_pic_path = os.path.join(destination_folder, "profile_pic.jpg")
    if os.path.exists(profile_pic_path):
        client.account_change_picture(profile_pic_path)
        print("Profile picture uploaded!")
    else:
        print("No profile picture to upload.")
    
    # Update bio
    client.account_set_biography(bio)
    print("Bio updated!")
    
    # Upload posts
    posts_folder = os.path.join(destination_folder, "posts")
    if not os.path.exists(posts_folder):
        print("No posts to upload.")
        return

    for post_file in os.listdir(posts_folder):
        try:
            if post_file.endswith(".jpg") or post_file.endswith(".png"):
                post_path = os.path.join(posts_folder, post_file)
                caption = f"Uploaded from {target_username}'s account."
                client.photo_upload(post_path, caption=caption)
                print(f"Uploaded post: {post_file}")
        except Exception as e:
            print(f"Failed to upload {post_file}: {e}")
    print("All posts uploaded successfully!")


def main():
    print("Instagram Profile Cloner")
    
    # Inputs
    source_username = input("Enter the source Instagram username: ")
    target_username = input("Enter the target Instagram username: ")
    cookies_path = os.path.join(os.path.dirname(__file__), "cookies.txt")

    # Create folders
    destination_folder = f"cloned_{source_username}"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Login to Instagram using instagrapi
    client = Client()
    try:
        with open(cookies_path, "r") as f:
            cookies_content = f.read()
        sessionid = cookies_content.split("sessionid\t")[1].split("\n")[0]
        client.login_by_sessionid(sessionid)
        print("Logged in successfully!")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # Use Instaloader to fetch source profile details
    loader = Instaloader()
    try:
        profile = Profile.from_username(loader.context, source_username)
    except Exception as e:
        print(f"Failed to load profile: {e}")
        return

    # Download profile picture and posts
    download_profile_picture(profile, destination_folder)
    download_posts(profile, destination_folder, loader)

    # Upload to target account
    upload_to_target_account(client, destination_folder, target_username, profile.biography)


if __name__ == "__main__":
    main()
