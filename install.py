import os
import requests
import tqdm


def download_file(windows_link, mac_link, linux_link, filename):
  if os.name == "Windows":
    download_link = windows_link
  elif os.name == "posix":
    download_link = mac_link
  elif os.name == "Linux":
    download_link = linux_link
  else:
    print(f"OS {os.name} not supported. File not downloaded.")
    return

  response = requests.get(download_link, stream=True)

  if response.status_code == 200:
    file_size = int(response.headers.get('Content-Length', 0))

    with tqdm.tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
      with open(filename, "wb") as f:
        for chunk in response.iter_content(1024):
          if chunk:
            f.write(chunk)
            progress_bar.update(len(chunk))
  else:
    print(f"Download failed. Status code: {response.status_code}")


if __name__ == "__main__":
    download_file(
        "http://virtual-home.org//release/simulator/v2.0/v2.3.0/windows_exec.zip",
        "http://virtual-home.org/release/simulator/v2.0/v2.3.0/macos_exec.zip",
        "http://virtual-home.org//release/simulator/v2.0/v2.3.0/linux_exec.zip",
        "virtualhome/virtualhome/bin/simulator"
    )

