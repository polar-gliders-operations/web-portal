while inotifywait -r /home/mduplessis/web-portal/web-portal/data-plot/img/*; do
    echo erie9uMo | sudo -S rsync -avz /home/mduplessis/web-portal/web-portal/data-plot/img/map_overview.gif /var/www/roammiz.com/img/wind_movie.gif
done

