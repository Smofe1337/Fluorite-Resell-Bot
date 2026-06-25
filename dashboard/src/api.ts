import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:1337/api/'

const getToken = (name: string = "access_token"): string | null => {
  const cookies = document.cookie.split(';').map(cookie => cookie.trim());
  for (const cookie of cookies) {
    if (cookie.startsWith(`${name}=`)) {
      return cookie.substring(name.length + 1);
    }
  }
  return null;
};

export const getAllUsers = async () => {
    const response = await axios.get(
        BASE_URL + 'users/',
        {
            headers: {
                Authorization: `Bearer ${getToken()}`,
            }
        }
    );
    return response.data;
};

export const setBanStatus = async (userId: number, isBanned: boolean) => {
    return axios.post(
        BASE_URL + 'users/set-ban-status/',
        {
            user_id: userId,
            status: isBanned
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const setVipStatus = async (userId: number, isVip: boolean) => {
    return axios.post(
        BASE_URL + 'users/set-vip-status/',
        {
            user_id: userId,
            status: isVip
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const updateBalance = async (userId: number, amount: number, operator: string) => {
    return axios.post(
        BASE_URL + 'users/update-balance/', 
        {
            user_id: userId,
            amount: amount,
            operator: operator
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const getAllKeys = async () => {
    const response = await axios.get(
        BASE_URL + 'keys/',
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
    return response.data;
};

export const addKeys = async (game_name: string, duration: number, keys: string[]) => {
    const response = await axios.post(
        BASE_URL + 'keys/add/', 
        {
            keys: keys,
            game_name: game_name,
            duration: duration
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
    return response.data;
};

export const getAllGames = async () => {
    const response = await axios.get(
        BASE_URL + 'games/',
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
    return response.data;
};

export const deleteKey = async (key: string) => {
    await axios.post(
        BASE_URL + 'keys/delete/',
        {
            key: key
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const getKeysStats = async () => {
    const response = await axios.get(BASE_URL + 'keys/stats/', {
        headers: {
            Authorization: `Bearer ${getToken()}`,
        },
    });
    return response.data;
};

export const updateKeyStatus = async (key: string, status: string) => {
    await axios.post(
        BASE_URL + 'keys/update-status/',
        { key, status },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const deleteGame = async(name: string) => {
    await axios.post(
        BASE_URL + 'games/delete/', 
        {
            game_name: name
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

interface Pricing {
    day: number;
    week: number;
    month: number;
}

export const createGame = async(
    gameName: string,
    pricing: Pricing,
    imageUrl: string, 
    status: string,
    isNeedShowImg: boolean
) => {
    return await axios.post(
        BASE_URL + 'games/create/', 
        {
            game_name: gameName,
            pricing: {
                day: pricing.day,
                week: pricing.week,
                month: pricing.month
            },
            image_url: imageUrl,
            status: status,
            is_need_show_img: isNeedShowImg,
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const updateGame = async(
    gameName: string, 
    name: string,
    pricing: Pricing,
    imageUrl: string,
    status: string,
) => {
    await axios.post(
        BASE_URL + 'game/update/', 
        {
            updating_game: gameName,
            name: name,
            pricing: pricing,
            image_url: imageUrl,
            status: status
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const updateVisibility = async(gameName: string, isVisible: boolean) => {
    await axios.post(
        BASE_URL + 'game/update-visibility/', 
        {
            updating_game: gameName,
            status: isVisible
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const authorization = async(username: string, password: string) => {
    return await axios.post(
        BASE_URL + 'dashboard/auth/',
        {
            username: username,
            password: password
        },
    );
};

export const tokenValidator = async(token: string) => {
    return await axios.post(BASE_URL + 'dashboard/validate-token/', {
        token: token
    });
};

export const getAllOrders = async (
    page: number = 1,
    perPage: number = 15,
    search?: string,
    status?: string,
) => {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if (search) params.search = search;
    if (status && status !== 'all') params.status = status;

    const response = await axios.get(BASE_URL + 'orders/', {
        headers: {
            Authorization: `Bearer ${getToken()}`,
        },
        params,
    });

    return response.data;
};

export const getOrdersStats = async () => {
    const response = await axios.get(BASE_URL + 'orders/stats/summary/', {
        headers: {
            Authorization: `Bearer ${getToken()}`,
        },
    });
    return response.data;
};

export const uploadImage = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(BASE_URL + 'upload/image/', formData, {
        headers: {
            Authorization: `Bearer ${getToken()}`,
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data.url;
};

export const updateOrderStatus = async(order_id: string, status: string) => {
    await axios.post(
        BASE_URL + 'orders/update-status/',
        {
            order_id: order_id,
            status: status,
        },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`
            }
        }
    );
};

export const startBroadcast = async (
    text: string,
    photos: string[],
    buttons: { text: string; url: string }[],
) => {
    const response = await axios.post(
        BASE_URL + 'broadcast/send/',
        { text, photos, buttons },
        {
            headers: {
                Authorization: `Bearer ${getToken()}`,
            },
        }
    );
    return response.data;
};

export const getBroadcastStatus = async () => {
    const response = await axios.get(BASE_URL + 'broadcast/status/', {
        headers: {
            Authorization: `Bearer ${getToken()}`,
        },
    });
    return response.data;
};
