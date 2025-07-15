

    document.addEventListener("DOMContentLoaded", function () {
        const swipers = document.querySelectorAll('.swiper');
        const botonnext=document.querySelector('.swiper-button-next')
        const botonprev=document.querySelector('.swiper-button-prev')
        botonnext.style.color="transparent";
        botonprev.style.color="transparent";
        swipers.forEach((swiperEl) => {
            new Swiper(swiperEl, {
                navigation: {
                    nextEl: swiperEl.querySelector('.swiper-button-next'),
                    prevEl: swiperEl.querySelector('.swiper-button-prev'),
                    
                },
                loop: true,
                autoplay: {
                    delay: 3000, // Change image every 3 seconds
                    disableOnInteraction: false, // Continue autoplay even if user interacts

                },
            });
        });
    });

    let lightbox = document.getElementById("lightbox");
    let lightboxImg = document.getElementById("lightbox-img");
    let images = [];
    let currentIndex = 0;

    function openLightbox(url) {
        images = Array.from(document.querySelectorAll("img[onclick^='openLightbox']")).map(img => img.src);
        currentIndex = images.indexOf(url);
        lightboxImg.src = url;
        lightbox.style.display = "flex";
    }

    function closeLightbox() {
        lightbox.style.display = "none";
    }

    function changeLightbox(direction, event) {
        event.stopPropagation(); // Prevent event from bubbling up to close modal
        currentIndex = (currentIndex + direction + images.length) % images.length;
        lightboxImg.src = images[currentIndex];
    }

//CAMBIAR TEXTO DEL SUMMARY
    const cambiarTexto = document.querySelector(".summary-info");
    const defaultText = cambiarTexto.textContent;
    
    cambiarTexto.addEventListener("click", () => {
        if (cambiarTexto.textContent === "Cerrar") {
            cambiarTexto.textContent = defaultText;
        } else {
            cambiarTexto.textContent = "Cerrar";
        }
    });
    
    


    
