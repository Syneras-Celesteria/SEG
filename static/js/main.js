// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Nếu đang ở trang chủ thì load phim phổ biến
    if (document.getElementById('popularMovies')) {
        loadPopularMovies();
    }

    // Khởi tạo gợi ý tìm kiếm
    initSearchSuggestions();
});

function loadPopularMovies() {
    const container = document.getElementById('popularMovies');
    
    fetch('/api/popular-movies')
        .then(response => response.json())
        .then(data => {
            if (data.movies && data.movies.length > 0) {
                // 1. Tạo cấu trúc HTML cho Carousel
                let html = `
                    <div class="movie-carousel-wrapper">
                        <button class="scroll-btn scroll-left" onclick="scrollCarousel(-300)">
                            <i class="fas fa-chevron-left"></i>
                        </button>

                        <div class="scrolling-wrapper" id="movieScrollContainer">
                `;

                // 2. Loop qua từng phim
                data.movies.forEach(movie => {
                    html += `
                        <div class="card-fixed-width">
                            <div class="card h-100 movie-card">
                                <a href="${movie.url}" target="_blank" class="text-decoration-none text-dark">
                                    <div class="position-relative">
                                        <img src="${movie.poster_url || '/static/images/no-poster.jpg'}" 
                                             class="card-img-top" 
                                             alt="${movie.title}"
                                             style="height: 280px; object-fit: cover;" 
                                             onerror="this.src='https://via.placeholder.com/200x280?text=No+Poster'">
                                        
                                        <div class="movie-rating">
                                            <i class="fas fa-star text-warning"></i> ${movie.rating || 'N/A'}
                                        </div>
                                    </div>
                                    <div class="card-body p-2">
                                        <h6 class="card-title text-truncate mb-1" title="${movie.title}" style="font-size: 0.95rem;">
                                            ${movie.title}
                                        </h6>
                                        <p class="card-text small text-muted mb-0">
                                            ${movie.year} • ${movie.genre ? movie.genre.split(',')[0] : 'Phim'}
                                        </p>
                                    </div>
                                </a>
                            </div>
                        </div>
                    `;
                });

                // 3. Đóng thẻ và thêm nút lướt phải
                html += `
                        </div>
                        <button class="scroll-btn scroll-right" onclick="scrollCarousel(300)">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                `;

                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="col-12 text-center"><p>Chưa có dữ liệu phim.</p></div>';
            }
        })
        .catch(error => {
            console.error('Error loading popular movies:', error);
            container.innerHTML = '<div class="col-12 text-center text-danger"><p>Lỗi tải dữ liệu.</p></div>';
        });
}

// Hàm hỗ trợ scroll khi bấm nút
function scrollCarousel(offset) {
    const container = document.getElementById('movieScrollContainer');
    if (container) {
        container.scrollBy({ left: offset, behavior: 'smooth' });
    }
}

function initSearchSuggestions() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('suggestions');
    
    if (!searchInput || !suggestionsBox) return;

    let timeoutId;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(timeoutId);
        
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }

        // Debounce: chờ 300ms sau khi gõ xong mới gọi API
        timeoutId = setTimeout(() => {
            fetch(`/api/suggestions?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.suggestions && data.suggestions.length > 0) {
                        const listGroup = suggestionsBox.querySelector('.list-group');
                        listGroup.innerHTML = data.suggestions.map(text => 
                            `<a href="/search?q=${encodeURIComponent(text)}" class="list-group-item list-group-item-action">
                                <i class="fas fa-search text-muted me-2"></i>${text}
                            </a>`
                        ).join('');
                        suggestionsBox.style.display = 'block';
                    } else {
                        suggestionsBox.style.display = 'none';
                    }
                });
        }, 300);
    });

    // Ẩn suggestions khi click ra ngoài
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });
}