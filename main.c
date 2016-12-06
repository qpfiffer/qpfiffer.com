// vim: noet ts=4 sw=4
#include <string.h>
#include <time.h>

#include <38-moths/38-moths.h>

int main_sock_fd;

static int index_handler(const http_request *request, http_response *response) {
	greshunkel_ctext *ctext = gshkl_init_context();
	/* gshkl_add_int(ctext, "UPTIME", difftime(now, start_time)); */
	gshkl_add_string(ctext, "BG_IMAGE", "../static/img/bg.jpg");
	gshkl_add_string(ctext, "BG_IMAGE_SRC", "http://www.flickr.com/photos/104820964@N07/11595685883/");
	return render_file(ctext, "./templates/default.html", response);
}

static const route all_routes[] = {
	{"GET", "root_handler", "^/$", 0, &index_handler, &heap_cleanup},
};

int main(int argc, char *argv[]) {
	http_serve(&main_sock_fd, 8661, 2, all_routes, sizeof(all_routes)/sizeof(all_routes[0]));
	return 0;
}
