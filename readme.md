


# animerecon-benchmark

This repo downloads the AnimeRecon benchmark dataset introduced in [PAniC-3D: Stylized Single-view 3D Reconstruction from Portraits of Anime Characters](https://github.com/ShuhongChen/panic3d-anime-reconstruction).  As described in that repo, this downloader will add to `./_data/lustrous`


## setup

Make a copy of `./_env/machine_config.bashrc.template` to `./_env/machine_config.bashrc`, and set `$PROJECT_DN` to the absolute path of this repository folder.  The other variables are optional.

Run these lines from the project directory to pull the image from the main project and enter a container; note these are bash scripts inside the `./make` folder, not `make` commands.

    make/docker_pull
    make/shell_docker


## download

Download the `animerecon-benchmark.zip` from the project's [drive folder](https://drive.google.com/drive/folders/1Zpt9x_OlGALi-o-TdvBPzUPcvTc7zpuV?usp=share_link), and merge it with this repo's file structure.

### genshin 3d

    # run the downloader
    bash ./_scripts/download_genshin_3d.sh

### genshin 2d

    # run the downloader
    python3 -m _scripts.download_genshin_2d

### hololive 3d

    # follow the instructions in `./_scripts/download_hololive_3d.txt`

### hololive 2d

    # run the downloader
    python3 -m _scripts.download_hololive_2d


## citing

If you use our repo, please cite our work:

    @inproceedings{chen2023panic3d,
        title={PAniC-3D: Stylized Single-view 3D Reconstruction from Portraits of Anime Characters},
        author={Chen, Shuhong and Zhang, Kevin and Shi, Yichun and Wang, Heng and Zhu, Yiheng and Song, Guoxian and An, Sizhe and Kristjansson, Janus and Yang, Xiao and Matthias Zwicker},
        booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
        year={2023}
    }


