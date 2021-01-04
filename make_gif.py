import imageio
from os import walk


def make_gif(from_path: str, to_path: str, fps: int = 8) -> None:
    """ Turn all plots in from_path into a gif and save to to_path
    from_path: Directory to find plots
    to_path: Directory to save gif
    fps: Frames per second in gif
    """
    filenames = []
    for (dirpath, dirnames, fls) in walk(from_path):
        print(f"making gif of {len(fls)} images")
        filenames.extend(sorted(fls))
        break

    with imageio.get_writer(to_path, mode="I", fps=fps) as writer:
        for filename in filenames:
            image = imageio.imread(from_path + filename)
            writer.append_data(image)


if __name__ == "__main__":
    pth = './data/images/pm_2.5/'
    write_path = 'data/gifs/sensor_movie.gif'

    make_gif(pth, write_path)
